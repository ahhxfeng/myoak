package api

import (
	"context"
	"encoding/json"
	"fmt"
	"strconv"
	"time"

	"github.com/ahhxfeng/myoak/oak_collector/log"
	"github.com/ahhxfeng/myoak/oak_collector/storage"
	"github.com/gin-gonic/gin"
)

// type reportRequest struct {
// 	UserName     string                `json:"account,omitempty"`
// 	DeviceId     string                `json:"device,omitempty"`
// 	HashRate     *map[string][]float64 `json:"hashrate,omitempty"`
// 	Temperature  *[]int32              `json:"temperature,omitempty"`
// 	GpuFrequency *[]int32              `json:"gpu_freq,omitempty"`
// 	MemFrequency *[]int32              `json:"mem_freq,omitempty"`
// 	GpuCount     *int32                `json:"gpu_count,omitempty"`
// 	FanSpeed     *int32                `json:"fan_speed,omitempty"`
// 	TagName      string                `json:"tag_name,omitempty"`
// }

type reportRequest struct {
	UserName     string                `json:"account"`
	DeviceId     string                `json:"device"`
	HashRate     *map[string][]float64 `json:"hashrate"`
	Temperature  *[]int32              `json:"temperature"`
	GpuFrequency *[]int32              `json:"gpu_freq"`
	MemFrequency *[]int32              `json:"mem_freq"`
	GpuCount     *int32                `json:"gpu_count"`
	FanSpeed     *[]int32              `json:"fan_speed"`
	TagName      string                `json:"tag_name"`
}

type User struct {
	UserName string `json:"user"`
}

func OnReport(c *gin.Context) {
	if c.Request.Method == "GET" {
		c.JSON(400, FormatReponse.NewResponse(400, "method not allow ", ""))
		return
	}

	reportData := reportRequest{}

	if err := c.ShouldBindJSON(&reportData); err != nil {
		log.Logger.Warn(err.Error())
		c.JSON(500, FormatReponse.NewResponse(500, "internal error", ""))
		return
	}
	// } else {
	// 	// debug
	// 	// c.JSON(200, FormatReponse.NewResponse(200, "success bind", reportData))
	// 	// log.Logger.Warn("try to print the request", reportData)
	// 	// return
	// }

	if reportData.UserName == "" || reportData.DeviceId == "" {
		// debug
		log.Logger.Warn("try to print the request", reportData)

		c.JSON(400, FormatReponse.NewResponse(400, "empty parmter", ""))
		return
	}

	fmt.Printf("report username%s", reportData.UserName)
	user, ok := storage.DbCheckUserPrivilege(reportData.UserName)
	if !ok {
		c.JSON(404, FormatReponse.NewResponse(404, "no such account", ""))
		return
	}

	_, ok = storage.DbCheckRigPrivilege(user, reportData.DeviceId)
	if !ok {
		c.JSON(404, FormatReponse.NewResponse(404, "no such rig", ""))
		return
	}

	// async ,post hook
	// cCp = c.Copy()
	go func() {
		safeUserName := storage.SafeStatsdKey(reportData.UserName)
		safeDeviceId := storage.SafeStatsdKey(reportData.DeviceId)
		storage.Statsd.Incr(fmt.Sprintf("req.report.user."+safeUserName+".avg"), 1)
		storage.Statsd.Incr(fmt.Sprintf("req.report.user."+safeUserName+".device."+safeDeviceId+".avg"), 1)
		updateRedis := make([]interface{}, 0, 3)

		updateRedis = append(updateRedis, "redis-key-placeholder")

		// report time
		updateRedis = append(updateRedis, "ts")
		updateRedis = append(updateRedis, strconv.FormatInt(time.Now().Unix(), 10))

		// report hashrate
		if reportData.HashRate != nil {
			totalHashRate := sumHashList(*reportData.HashRate)
			for k, v := range totalHashRate {
				safeKey := storage.SafeStatsdKey(k)
				storage.Statsd.Gauge("req.report.user."+safeUserName+".device."+safeDeviceId+".hash_sum."+safeKey, int64(v))
			}
			updateRedis = append(updateRedis, "hash")
			jsonString, _ := json.Marshal(reportData.HashRate)
			updateRedis = append(updateRedis, string(jsonString))

		}

		// report temperature
		if reportData.Temperature != nil {

			_, maxTemperature, _ := statInNumList(*reportData.Temperature)
			storage.Statsd.Gauge("req.report.user."+safeUserName+".device."+safeDeviceId+".temp_max", int64(maxTemperature))
			jsonString, _ := json.Marshal(*reportData.Temperature)
			updateRedis = append(updateRedis, "temp")
			updateRedis = append(updateRedis, string(jsonString))
		}

		// 保存gpu_freq
		if reportData.GpuFrequency != nil {
			jsonString, _ := json.Marshal(*reportData.GpuFrequency)
			updateRedis = append(updateRedis, "gpu")
			updateRedis = append(updateRedis, string(jsonString))
		}

		// 保存mem_freq
		if reportData.MemFrequency != nil {
			jsonString, _ := json.Marshal(*reportData.MemFrequency)
			updateRedis = append(updateRedis, "mem")
			updateRedis = append(updateRedis, string(jsonString))
		}

		// 保存gpu_num
		if reportData.GpuCount != nil {
			jsonString, _ := json.Marshal(*reportData.GpuCount)
			updateRedis = append(updateRedis, "ngpu")
			updateRedis = append(updateRedis, string(jsonString))
		}

		// 保存fan_speed
		if reportData.FanSpeed != nil {
			jsonString, _ := json.Marshal(*reportData.FanSpeed)
			updateRedis = append(updateRedis, "fan")
			updateRedis = append(updateRedis, string(jsonString))
		}
		// 保存tag_name
		if reportData.TagName != "" {
			jsonString, _ := json.Marshal(reportData.TagName)
			updateRedis = append(updateRedis, "tag_name")
			updateRedis = append(updateRedis, string(jsonString))
		}

		if len(updateRedis) > 1 {
			log.Logger.Info("report: \n", "user: ", reportData.UserName, "device: ", reportData.DeviceId, "info", updateRedis)
			ctx := context.Background()
			err := storage.RedisUpdateRig(ctx, reportData.DeviceId, updateRedis)
			if err != nil {
				log.Logger.Warn(err.Error())
				return
			}
		}

		// 心跳
		log.Logger.Info("\n try to touch new rigs \n")
		storage.DbTouchRig(user, reportData.DeviceId)
		storage.RedisTouchRig(context.Background(), reportData.DeviceId)

	}()

}

// {"eth": [33, 33, 33]} => {"eth": 99}
func sumHashList(input map[string][]float64) map[string]float64 {
	res := make(map[string]float64)
	for key, v := range input {
		var sum float64
		for _, i := range v {
			sum = sum + i
		}
		res[key] = sum
	}
	return res
}

// [1,2,3] => (1,3,6)
func statInNumList(input []int32) (min int32, max int32, sum int32) {
	if len(input) > 0 {
		min = input[0]
		max = input[0]
	}
	for _, value := range input {
		if max < value {
			max = value
		}
		if min > value {
			min = value
		}
		sum += value
	}
	return
}
