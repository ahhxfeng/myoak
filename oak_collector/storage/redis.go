package storage

//TODO
import (
	"context"

	"github.com/ahhxfeng/myoak/oak_collector/config"
	"github.com/ahhxfeng/myoak/oak_collector/log"
	"github.com/redis/go-redis/v9"
)

var (
	RedisClient *redis.Client
)

func InitRedis() (RedisClient *redis.Client) {
	rdb := redis.NewClient(&redis.Options{
		Addr:         config.Conf.RedisAddress,
		MaxIdleConns: config.Conf.RedisMaxIdle,
	},
	)

	log.Logger.Info("Redis init success")
	return rdb
}

func RedisTouchRig(ctx context.Context, deviceId string) error {
	// 延长RIG信息的保存时间，返回0 如果key不存在
	key := "rig:" + deviceId
	_, err := RedisClient.Do(ctx, "EXPIRE", key, config.Conf.RedisRigTtl).Result()
	return err
}

func RedisUpdateRig(ctx context.Context, deviceId string, args []interface{}) error {
	// 更新rig信息。返回0如果key不存在的话。args[0]空出不要填，args[2n+1] = field，args[2n+2] = value

	key := "rig:" + deviceId
	args[0] = key

	_, err := RedisClient.Do(ctx, "HMSET", args).Result()
	return err
}

func RedisPushCommand(ctx context.Context, deviceId string, command string) error {
	// Push command
	key := "cmd:" + deviceId
	_, err := RedisClient.Do(ctx, "SADD", key, command).Result()

	return err
}

func RedisPopCommand(ctx context.Context, deviceId string) (result interface{}, err error) {
	// Pop command
	key := "cmd:" + deviceId
	result, err = RedisClient.Do(ctx, "SMEMBERS", key).Result()
	RedisClient.Do(ctx, "DEL", key)
	return result, err
}

func RedisTouchCommand(ctx context.Context, deviceId string, command string) error {
	// 延长command信息保存时间
	key := "cmd:" + deviceId
	_, err := RedisClient.Do(ctx, "EXPIRE", key, command).Result()
	return err
}
