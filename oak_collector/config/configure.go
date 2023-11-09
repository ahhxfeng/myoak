package config

import (
	"encoding/json"
	"io/ioutil"
	"os"
)

// type GlobalConfig struct {
// 	// listen server
// 	PublicAddress  string ` : "0.0.0.0:12927"`
// 	PrivateAddress string `default: "0.0.0.0:12926"`

// 	// sign pipe
// 	SignPipePrivateKeyPath  string   `default: "./key_selected"`
// 	AvailableCommand        []string `default: "reboot, config"`
// 	LongPoolingTime         int      `default: 15`
// 	LongPoolingNotifyBucket int      `default: 10000`
// 	UploadDir               string   `default: ./upload`
// 	UploadLimmit            int      `default: 1000000`

// 	//version
// 	VersionName string `default: 1`
// 	VersionUrl  string `default: "www.baidu.com"`
// 	VersionMd5  string `default: "d41d8cd98f00b204e9800998ecf8427e"`

// 	// db
// 	DatabaseDsn              string `default: "dburl"`
// 	DatabaseDriver           string `default: "mysql"`
// 	DatabaseDownloadInterval int    `default: 60`
// 	DatabaseUploadInterval   int    `default: 5`

// 	// Redis
// 	RedisAddress     string `default: "redis url"`
// 	RedisMaxIdle     int    `defualt: 64`
// 	RedisIdleTimeout int    `default: 60`
// 	RedisRigTtl      int    `default: 604800` // rig信息保存多少秒
// 	RedisCmdTtl      int    `default: 60`     //Cmd 信息保存多少秒
// 	// log
// 	LogDir      string `default: log`
// 	LogLevel    string `default: debug`
// 	WinLogLevel string `default: debug`

// 	//statsd

// 	StatsdAddress string `default: "statsdURl"`
// 	StatsdPrefix  string `default: "oak"`
// }

type GlobalConfig struct {
	// listen server
	PublicAddress  string `json:"public_address"`
	PrivateAddress string `json: "private_address"`

	// sign pipe
	SignPipePrivateKeyPath  string   `json: "private_key_path"`
	AvailableCommand        []string `json: "availabel_command"`
	LongPoolingTime         int      `json: "long_pooling_time"`
	LongPoolingNotifyBucket int      `json: "long_pooling_notify_bucket"`
	UploadDir               string   `json: "upload_dir"`
	UploadLimmit            int      `json: "upload_limmit"`

	//version
	VersionName string `json: "version_name"`
	VersionUrl  string `json: "version_url"`
	VersionMd5  string `json: "version_md5"`

	// db
	DatabaseDsn              string `json: "database_url"`
	DatabaseDriver           string `json: "database_driver"`
	DatabaseDownloadInterval int    `json: "database_download_interval"`
	DatabaseUploadInterval   int    `json: "database_upload_interval"`

	// Redis
	RedisAddress     string `json: "redis_url"`
	RedisMaxIdle     int    `defualt: "redis_max_idle"`
	RedisIdleTimeout int    `json: "redis_idle_timeout"`
	RedisRigTtl      int    `json: "redis_rig_ttl"` // rig信息保存多少秒
	RedisCmdTtl      int    `json: redis_cmd_ttl`   //Cmd 信息保存多少秒
	// log
	LogDir      string `json: "log_dir"`
	LogLevel    string `json: "log_level"`
	WinLogLevel string `json: "win_log_level"`

	//statsd

	StatsdAddress string `json: "statsdURl"`
	StatsdPrefix  string `json: "statsd_prefix"`
}

func NewConfig() *GlobalConfig {
	config := &GlobalConfig{}
	return config
}

func (c *GlobalConfig) LoadFromFile(file string) error {
	f, err := os.Open(file)
	if err != nil {
		return err
	}

	content, err := ioutil.ReadAll(f)
	if err != nil {
		return err
	}
	if err := json.Unmarshal(content, c); err != nil {
		return err
	}
	return nil
}

func (c *GlobalConfig) SaveToFile(file string) error {
	f, err := os.Create(file)
	if err != nil {
		return err
	}
	content, err := json.Marshal(c)
	if err != nil {
		return err
	}
	// f.Write(content)
	if _, err := f.Write(content); err != nil {
		return err
	}
	return nil
}

func (c *GlobalConfig) String() string {
	content, err := json.Marshal(c)
	if err != nil {
		return err.Error()
	}
	return string(content)
}

var Conf = NewConfig()
