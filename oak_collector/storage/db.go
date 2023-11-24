package storage

import (
	"database/sql"
	"sync"
	"time"

	"github.com/ahhxfeng/myoak/oak_collector/config"
	"github.com/ahhxfeng/myoak/oak_collector/log"
	"gorm.io/driver/mysql"
	"gorm.io/gorm"
)

var (
	Db            *gorm.DB
	cacheLock     *sync.Mutex
	userCache     map[string]*User  // username -> user
	rigCache      map[string]*Rig   // deviceId -> Rig
	dirtyRig      map[string]*Rig   // deviceId -> rig
	rigGroupCache map[int]*RigGroup // rigGroupId -> RigGroup
)

type User struct {
	Id       int    `gorm:"column:id"`
	UserName string `gorm:"column:user_name"`
	Status   string `gorm:"column:status"`
}

type Rig struct {
	Id         int    `gorm:"column:id"`
	UserId     int    `gorm:"column:user_id"`
	RigGroupId *int   `gorm:"column:rig_group_id"`
	DeviceId   string `gorm:"column:device_id"`
	Status     string `gorm:"column:status"`
}

type RigGroup struct {
	Id     int    `gorm:"column:id"`
	UserId int    `gorm:"column:user_id"`
	Config string `gorm:"column:config"`
	Status string `gorm:"column:status"`
}

func InitDb() {
	userCache := make(map[string]*User)
	rigCache := make(map[string]*Rig)
	dirtyRig := make(map[string]*Rig)
	rigGroupCache := make(map[string]*RigGroup)

	go func() {
		for {
			DbDownload()
			time.Sleep(time.Duration(config.Conf.DatabaseDownloadInterval) * time.Second)
		}
	}()

	go func() {
		for {
			DbUpload()
			time.Sleep(time.Duration(config.Conf.DatabaseUploadInterval) * time.Second)
		}
	}()

}

func ConnectIfNil() (Db *gorm.DB, err error) {
	// dsn := "user:pass@tcp(127.0.0.1:3306)/dbname?charset=utf8mb4&parseTime=True&loc=Local"
	// dsn := //think:123456@localhost/oak?charset=utf8"
	dsn := "think:123456@tcp(127.0.0.1:3306)/oak?charset=utf-8mb4&parseTime=True&loc=Local"
	SqlDB, err := sql.Open("mysql", dsn)
	if err != nil {
		log.Logger.Info("mysql connect fialed")
		log.Logger.Error(err.Error())
		return nil, err
	}
	GormDB, err := gorm.Open(mysql.New(mysql.Config{
		Conn: SqlDB,
	}), &gorm.Config{})
	if err != nil {
		log.Logger.Info("gorm init failed")
		log.Logger.Error(err.Error())
		return nil, err
	}
	return GormDB, nil
}

func DbDownload() {
	// Db 全量更新 慢！
	log.Logger.Info("Db downlaod start !")
	defer func() {
		log.Logger.Info("Db downlaod complted: got %d users %d rigs %d rigGroups", len(userCache), len(rigCache), len(rigGroupCache))
	}()

	Db, err := ConnectIfNil()
	if err != nil {
		return
	}

	// user
	newUserCache := make(map[string]*User)
	err = func() error {
		rows, err := Db.Table("oak_user").Select("id", "user_name", "status").Rows()
		if err != nil {
			log.Logger.Warn(err.Error())
			return err
		}
		defer rows.Close()
		for rows.Next() {
			item := &User{}
			err = rows.Scan(item.Id, item.UserName, item.Status)
			if err != nil {
				log.Logger.Warn(err.Error())
				continue
			}
			newUserCache[item.UserName] = item
		}
		return nil

	}()

	if err != nil {
		log.Logger.Warn("update oak_user failed", err.Error())
		return
	}

	// Rig

	newDeviceCache := make(map[string]*Rig)

	err = func() error {
		rows, err := Db.Table("oak_rig").Select("id", "user_id", "rig_group_id", "device_id").Rows()
		if err != nil {
			log.Logger.Warn(err.Error())
			return err
		}
		defer rows.Close()
		for rows.Next() {
			item := &Rig{}
			err = rows.Scan(item.Id, item.UserId, item.RigGroupId, item.DeviceId)
			if err != nil {
				log.Logger.Warn(err.Error())
				continue
			}
			newDeviceCache[item.DeviceId] = item
		}
		return nil
	}()

	// RigGroup

	newRigGroupCache := make(map[int]*RigGroup)
	err = func() error {
		rows, err := Db.Table("oak_rig_group").Select("id", "user_id", "config", "status").Rows()
		if err != nil {
			log.Logger.Warn(err.Error())
			return err
		}
		defer rows.Close()
		for rows.Next() {
			item := &RigGroup{}
			err = rows.Scan(item.Id, item.UserId, item.Config, item.Status)
			if err != nil {
				log.Logger.Warn(err.Error())
				continue
			}
			newRigGroupCache[item.Id] = item
		}
		return nil
	}()

	//save
	cacheLock.Lock()
	userCache = newUserCache
	rigCache = newDeviceCache
	rigGroupCache = newRigGroupCache
	cacheLock.Unlock()
}

func DbUpload() {
	//TODO
	cacheLock.Lock()
	defer cacheLock.Unlock()
	if len(dirtyRig) == 0 {
		// 没有发现新的rig
		return
	}

	log.Logger.Info("Db upload start ! %d rig discovery", len(dirtyRig), dirtyRig)
	for _, rig := range dirtyRig {
		res := Db.Exec("insert into oak_rig (user_id, device_id, status) values (?, ?, ?)", rig.UserId, rig.DeviceId, rig.Status)
		res.Commit()
		// rig.Id = res.Last()

		// dirty 表移动到正式表
		delete(dirtyRig, rig.DeviceId)
		rigCache[rig.DeviceId] = rig
	}
	defer log.Logger.Info("Db upload end  !")

}

func DbCheckUserPrivilege(userName string) (user *User, ok bool) {
	cacheLock.Lock()
	defer cacheLock.Unlock()
	user, ok = userCache[userName]
	if !ok {
		log.Logger.Warn("user not found:", userName)
		return
	} else if user.Status != "normal" {
		ok = false
		return
	}
	return
}

// 不存在的rig不会报错（discovery的场景）
func DbCheckRigPrivilege(user *User, deviceId string) (rig *Rig, ok bool) {
	cacheLock.Lock()
	defer cacheLock.Unlock()
	rig, ok = rigCache[deviceId]
	if !ok {
		rig, ok = dirtyRig[deviceId]
	}
	if !ok {
		// 这是discovery场景
		ok = true
		return
	}
	if rig.UserId != user.Id {
		ok = false
		return
	}
	ok = true
	return
}

func DbTouchRig(user *User, deviceId string) {
	cacheLock.Lock()
	defer cacheLock.Unlock()
	_, ok := rigCache[deviceId]
	if ok {
		return
	}
	_, ok = dirtyRig[deviceId]
	if ok {
		return
	}

	// new rig insert into dirtyrig first
	dirtyRig[deviceId] = &Rig{
		UserId:   user.Id,
		DeviceId: deviceId,
		Status:   "new",
	}
}

func DbGetRig(deviceId string) *Rig {
	cacheLock.Lock()
	defer cacheLock.Unlock()
	rig, ok := rigCache[deviceId]
	if ok {
		return rig
	}
	rig, ok = dirtyRig[deviceId]
	if ok {
		return rig
	}
	return nil
}

func DbGetRigConfig(deviceId string) string {
	cacheLock.Lock()
	defer cacheLock.Unlock()
	rig, ok := rigCache[deviceId]
	if !ok {
		// 不必读dirty表，dirty表不可能有配置
		return "{}"
	}
	if rig.RigGroupId == nil {
		return "{}"
	}
	rigGroup, ok := rigGroupCache[*rig.RigGroupId]
	if !ok {
		return "{}"
	}
	return rigGroup.Config
}

func DbGetRigDeviceIdInRigGroup(rigGroupId int) (result []*Rig) {
	cacheLock.Lock()
	defer cacheLock.Unlock()
	result = make([]*Rig, 0)
	// s := `SELECT id, user_id, device_id, status FROM oak_rig WHERE rig_group_id = ?`
	// rows, err := Db.Q(s, rigGroupId)
	rows, err := Db.Table("oak_rig").Select("id", "user_id", "device_id", "status").Where("rig_group_id = ?", rigGroupId).Rows()
	if err != nil {
		log.Logger.Warn(err.Error())
		return
	}
	for rows.Next() {
		item := &Rig{}
		err = rows.Scan(&item.Id, &item.UserId, &item.DeviceId, &item.Status)
		if err != nil {
			log.Logger.Warn(err.Error())
			continue
		}
		item.RigGroupId = &rigGroupId
		result = append(result, item)
	}
	return

}
