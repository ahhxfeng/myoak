package api

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

func GetVersion(c *gin.Context) {
	if c.Request.Method == "GET" {
		// log.Logger.Error("method not allow")
		c.JSON(http.StatusBadRequest, FormatReponse.NewResponse(400, "methon not allow", ""))
	}
}
