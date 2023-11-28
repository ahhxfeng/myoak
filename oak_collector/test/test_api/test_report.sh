curl -POST -v 'http://localhost:8080/report' -d '{
  "account": "test",
  "device": "da39a3ee5e6b4b0d3255bfef95601890afd80709",
  "hashrate": {
    "eth": [33, 32, 33, 32.4]
  },
  "temperature": [
    67, 68, 69
  ],
  "gpu_freq": [
    900, 991, 992
  ],
  "mem_freq": [
    1070, 1090, 1080
  ],
  "fan_speed": [
    20, 30, 40
  ],
  "gpu_num": 6
}'
