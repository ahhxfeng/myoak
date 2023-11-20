package storage

import (
	"regexp"
	"time"

	"github.com/ahhxfeng/myoak/oak_collector/config"
	"github.com/ahhxfeng/myoak/oak_collector/log"
	"github.com/quipo/statsd"
)

var (
	statsdClient       *statsd.StatsdClient
	Statsd             *statsd.StatsdBuffer
	SafeStatsdKeyRegex *regexp.Regexp
)

func InitStatsd() {
	statsdClient = statsd.NewStatsdClient(config.Conf.StatsdAddress, config.Conf.StatsdPrefix)
	err := statsdClient.CreateSocket()
	if err != nil {
		log.Logger.Error(err.Error())
	}
	stats := statsd.NewStatsdBuffer(time.Second*2, statsdClient)
	defer stats.Close()

	SafeStatsdKeyRegex, err = regexp.Compile(`[^a-zA-Z0-9]`)
	if err != nil {
		log.Logger.Error(err.Error())
	}

}

func SafeStatsdKey(key string) string {
	return SafeStatsdKeyRegex.ReplaceAllString(key, "_")
}
