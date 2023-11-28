package api

import "github.com/gin-gonic/gin"

func OnIndex(c *gin.Context) {
	c.JSON(200, FormatReponse.NewResponse(200, "main index", "hello world !!"))
}
