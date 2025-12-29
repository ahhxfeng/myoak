#coding=utf-8

"""
oak-os.sysinfo 的 Docstring

"""

from os import system
import subprocess

#import GPUtil
import pynvml


def detect_video_system()->str:
    #MOUDLE_AMD=subprocess.check_output("lsmod | grep amdgpu | wc -l", shell=True)
    MOUDLE_AMD = 1
    if int(MOUDLE_AMD) > 0:
        return "AMD"
    MOUDLE_NVIDIA = subprocess.check_output("lsmod | grep nvidia | wc -l", shell=True)
    if int(MOUDLE_NVIDIA) > 0:
        return "NVIDIA"
    return "empty"

def get_video_card_info_d():
    """
    get_video_card_info_d 的 Docstring
    
    """
    sys_type = detect_video_system()
    if sys_type == "NVIDIA":
        gpus = GPUtil.getGPUs()
        print(gpus)
        info = []
        for gpu in gpus:
            info.append({"name": gpu.name,
                         "memory_total": gpu.memoryTotal,
                         "memory_used": gpu.memoryUsed,
                         "temperature": gpu.temperature
                         })
        return info
def get_video_card_info():
    """
    get_video_card_info 的 Docstring

    """
    sys_type = detect_video_system()
    if sys_type == "NVIDIA":
        pass

def gather_nvidia_card_info():
    """
    gather_nvidia_card_info
    use pynvml moudle
    @return info[core, memory, temp, fan]
    
    """

    try:
        # pynvml 初始化
        pynvml.nvmlInit()
        devices_count = pynvml.nvmlDeviceGetCount()
        print("检测到 {} 张显卡".format(devices_count))
        card_info = []
        for d in range(devices_count):
            # 获取设备句柄
            handle = pynvml.nvmlDeviceGetHandleByIndex(d)

            name = pynvml.nvmlDeviceGetName(handle)
            temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
            fan_speed = pynvml.nvmlDeviceGetFanSpeed(handle)
            memory = pynvml.nvmlDeviceGetMemoryInfo(handle)
            memory_clock = pynvml.nvmlDeviceGetClockInfo(handle, pynvml.NVML_CLOCK_MEM)

            card_info.append(dict(name=name, temp=temp, fan_speed=fan_speed, memory=memory, memory_clock=memory_clock))

        # 关闭 pynvml
        pynvml.nvmlShutdown()
    except pynvml.NVMLError as e:
        print("nvml Error {}".format(e))
    except Exception as e:
        print("exception {}".format(e))



        
if __name__ == "__main__":
    get_video_card_info()
