package storage

import (
	"database/sql"

	"github.com/ahhxfeng/myoak/oak_collector/log"
	"gorm.io/driver/mysql"
	"gorm.io/gorm"
)

type User struct {
	Id       int    `gorm:"column:id"`
	UserName string `gorm:"column:user_name"`
}

type Rig struct {
	Id         int    `gorm:"column:id"`
	UserId     int    `gorm:"column:user_id"`
	RigGroupId int    `gorm:"column:rig_group_id"`
	DeviceId   string `gorm:"column:device_id"`
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

}

func ConnectIfNil() error {
	dsn := "user:pass@tcp(127.0.0.1:3306)/dbname?charset=utf8mb4&parseTime=True&loc=Local"
	SqlDB, err := sql.Open("mysql", dsn)
	if err != nil {
		log.Logger.Info("mysql connect fialed")
		log.Logger.Error(err.Error())
		return err
	}
	GormDB, err := gorm.Open(mysql.New(mysql.Config{
		Conn: SqlDB,
	}), &gorm.Config{})
	if err != nil {
		log.Logger.Info("gorm init failed")
		log.Logger.Error(err.Error())
		return err
	}
	return nil
}

func DbDownload() {
	// Db 全量更新 慢！
	log.Logger.Info("Db downlaod start !")
	defer func() {
		log.Logger.Info("Db downlaod complted: got %d users %d rigs %d rigGroups", len(userCache), len(rigCache), len(rigGroupCache))
	}()

	if err := ConnectIfNil(); err != nil {
		return
	}

	// user
	newUserCache := make(map[string]*User)
	err := func() error {
		var users User
		GormDB.Find(&User)

	}
}
