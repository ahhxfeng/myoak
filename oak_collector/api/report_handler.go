package api

import "github.com/gin-gonic/gin"

func OnReport(c *gin.Context) {
	if c.Request.Method == "GET" {
		c.JSON(400, FormatReponse.NewResponse(400, "method not allow ", ""))
		return
	}
}
