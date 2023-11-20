package api

import (
	"io"

	"github.com/gin-gonic/gin"
)

type FromatResponse struct {
	Code int         `json:"code"`
	Msg  string      `json:"msg"`
	Data interface{} `json:"data"`
}

func (fr *FromatResponse) NewResponse(code int, msg string, data interface{}) *FromatResponse {
	return &FromatResponse{
		Code: code,
		Msg:  msg,
		Data: data,
	}
}

func SetupRouter() *gin.Engine {
	gin.SetMode(gin.ReleaseMode)
	gin.DefaultWriter = io.Discard
	r := gin.Default()

	// router
	r.GET("/version", GetVersion)

	return r
}

var FormatReponse FromatResponse
