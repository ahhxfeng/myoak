package main

import (
	"flag"
	"fmt"
	"net/http"
	"os"

	"github.com/ahhxfeng/myoak/oak_collector/config"
	. "github.com/ahhxfeng/myoak/oak_collector/log"
)

var (
	ConfigFilePath     string
	PrintConfigExample bool
	UpdateConfig       bool
	PublicMux          *http.ServeMux
	PrivateMux         *http.ServeMux
)

func init() {
	flag.StringVar(&ConfigFilePath, "config", "../config/oak_collector.json", "配置config路径")
	flag.BoolVar(&PrintConfigExample, "example", false, "打印配置文件样例, 可留作后续使用")
	flag.BoolVar(&UpdateConfig, "update", false, "更新配置文件")

}

func doConfig() (quit bool) {
	if PrintConfigExample {
		// config.Conf.String()
		fmt.Println(config.Conf.String())
		return true
	}
	err := config.Conf.LoadFromFile(ConfigFilePath)
	if err != nil {
		Logger.Error(err.Error())
		return false
	}
	if UpdateConfig {
		ConfigBackup := ConfigFilePath + ".bak"
		if err := os.Rename(ConfigFilePath, ConfigBackup); err != nil {
			Logger.Error("config backup failed")
			Logger.Error(err.Error())
		} else {
			Logger.Info("old config has rename to ")
			Logger.Info(ConfigBackup)
			Logger.Info("The active config now : ")
			Logger.Info(config.Conf.String())
			if err := config.Conf.SaveToFile(ConfigFilePath); err != nil {
				Logger.Error("Update and Save config file failed :")
				Logger.Error(err.Error())

			} else {
				Logger.Info("Update config file success")
			}
		}
		Logger.Info("Current active config :")
		Logger.Info(config.Conf.String())
		return true
	}
	return

}

// func initMux() {
// 	PublicMux := http.NewServeMux()
// 	PrivateMux := http.NewServeMux()

// 	PublicMux.Handle("/version", )
// }
