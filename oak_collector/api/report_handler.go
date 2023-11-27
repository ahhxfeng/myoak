package api

import (
	"fmt"

	"github.com/ahhxfeng/myoak/oak_collector/log"
	"github.com/ahhxfeng/myoak/oak_collector/storage"
	"github.com/gin-gonic/gin"
)

type reportRequest struct {
	UserName     string                `json:"account,omitempty"`
	DeviceId     string                `json:"device_id,omitempty"`
	HashRate     *map[string][]float64 `json:"hashrate,omitempty"`
	Temperature  *[]int32              `json:"temperature,omitempty"`
	GpuFrequency *[]int32              `json:"gpu_freq,omitempty"`
	MemFrequency *[]int32              `json:"mem_freq,omitempty"`
	GpuCount     *int32                `json:"gpu_count,omitempty"`
	FanSpeed     *int32                `json:"fan_speed,omitempty"`
	TagName      string                `json:"tag_name,omitempty"`
}

func OnReport(c *gin.Context) {
	if c.Request.Method == "GET" {
		c.JSON(400, FormatReponse.NewResponse(400, "method not allow ", ""))
		return
	}

	reportData := reportRequest{}

	if err := c.ShouldBind(&reportData); err != nil {
		log.Logger.Warn(err.Error())
		c.JSON(500, FormatReponse.NewResponse(500, "internal error", ""))
		return
	}

	if reportData.UserName == "" || reportData.DeviceId == "" {
		c.JSON(400, FormatReponse.NewResponse(400, "empty parmter", ""))
		return
	}

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
	cCp = c.Copy()
	go func() {
		safeUserName := storage.SafeStatsdKey(reportData.UserName)
		safeDeviceId := storage.SafeStatsdKey(reportData.DeviceId)
		storage.Statsd.Incr(fmt.Sprintf("req.report.user."+safeUserName+".avg"), 1)
		storage.Statsd.Incr(fmt.Sprintf("req.report.user."+safeUserName+".device."+safeDeviceId+".avg"), 1)
		updateRedis := make([]interface{}, 0, 3)
	}()

}
