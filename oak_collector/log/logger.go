package log

import (
	"log/slog"
	"os"
)

func getLogger(file string, level slog.Level) *slog.Logger {
	var programLevel = new(slog.LevelVar)
	opts := &slog.HandlerOptions{
		Level:     programLevel,
		AddSource: true,
	}
	logger := slog.New(slog.NewTextHandler(os.Stdout, opts))
	programLevel.Set(slog.LevelInfo)
	return logger
}

var Logger = getLogger("oak_collector.log", slog.LevelInfo)
