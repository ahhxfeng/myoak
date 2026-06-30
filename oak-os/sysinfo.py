#coding=utf-8

"""
Collect host CPU, memory and GPU information for oak-os.
"""

import os
import platform
import subprocess
import time

try:
    import pynvml
except Exception:
    pynvml = None


def _read_proc_stat():
    try:
        with open("/proc/stat", "r") as f:
            fields = f.readline().strip().split()[1:]
        values = [int(item) for item in fields]
        idle = values[3] + (values[4] if len(values) > 4 else 0)
        total = sum(values)
        return idle, total
    except Exception:
        return None


def get_cpu_info(sample_interval=0.1):
    cpu = {
        "processor": platform.processor() or platform.machine(),
        "architecture": platform.machine(),
        "core_count": os.cpu_count() or 0,
        "load_avg": None,
        "usage_percent": None,
    }

    if hasattr(os, "getloadavg"):
        try:
            cpu["load_avg"] = list(os.getloadavg())
        except Exception:
            pass

    first = _read_proc_stat()
    if first is not None:
        time.sleep(sample_interval)
        second = _read_proc_stat()
        if second is not None:
            idle_delta = second[0] - first[0]
            total_delta = second[1] - first[1]
            if total_delta > 0:
                cpu["usage_percent"] = round((1 - idle_delta / total_delta) * 100, 2)

    return cpu


def get_memory_info():
    if platform.system() == "Darwin":
        return _get_darwin_memory_info()

    meminfo = {}
    try:
        with open("/proc/meminfo", "r") as f:
            for line in f:
                key, value = line.split(":", 1)
                meminfo[key] = int(value.strip().split()[0]) * 1024
    except Exception:
        pass

    total = meminfo.get("MemTotal")
    available = meminfo.get("MemAvailable")
    free = meminfo.get("MemFree")
    used = None
    usage_percent = None

    if total is not None:
        if available is not None:
            used = total - available
        elif free is not None:
            used = total - free
        if used is not None:
            usage_percent = round(used * 100 / total, 2)

    return {
        "total": total,
        "available": available,
        "used": used,
        "usage_percent": usage_percent,
    }


def _get_darwin_memory_info():
    try:
        page_size = os.sysconf("SC_PAGE_SIZE")
        try:
            total = int(subprocess.check_output(["sysctl", "-n", "hw.memsize"], text=True, stderr=subprocess.DEVNULL).strip())
        except Exception:
            total = os.sysconf("SC_PHYS_PAGES") * page_size
        vm_stat = subprocess.check_output(["vm_stat"], text=True)
    except Exception:
        return {
            "total": None,
            "available": None,
            "used": None,
            "usage_percent": None,
        }

    pages = {}
    for line in vm_stat.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        try:
            pages[key.strip()] = int(value.strip().rstrip("."))
        except Exception:
            pass

    free_pages = pages.get("Pages free", 0) + pages.get("Pages inactive", 0)
    available = free_pages * page_size
    used = total - available
    return {
        "total": total,
        "available": available,
        "used": used,
        "usage_percent": round(used * 100 / total, 2) if total else None,
    }


def detect_video_system():
    if platform.system() == "Darwin":
        return "Darwin"

    try:
        modules = subprocess.check_output(["lsmod"], text=True)
    except Exception:
        return "empty"
    if "amdgpu" in modules:
        return "AMD"
    if "nvidia" in modules:
        return "NVIDIA"
    return "empty"


def gather_nvidia_card_info():
    if pynvml is None:
        return []

    card_info = []
    try:
        pynvml.nvmlInit()
        devices_count = pynvml.nvmlDeviceGetCount()
        for index in range(devices_count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(index)
            name = pynvml.nvmlDeviceGetName(handle)
            if isinstance(name, bytes):
                name = name.decode("utf-8", errors="replace")

            memory = pynvml.nvmlDeviceGetMemoryInfo(handle)
            card_info.append({
                "index": index,
                "vendor": "NVIDIA",
                "name": name,
                "temperature": pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU),
                "fan_speed": pynvml.nvmlDeviceGetFanSpeed(handle),
                "memory_total": memory.total,
                "memory_used": memory.used,
                "memory_clock": pynvml.nvmlDeviceGetClockInfo(handle, pynvml.NVML_CLOCK_MEM),
            })
    except Exception:
        return card_info
    finally:
        try:
            pynvml.nvmlShutdown()
        except Exception:
            pass
    return card_info


def gather_amd_card_info():
    return []


def gather_darwin_card_info():
    try:
        output = subprocess.check_output(["system_profiler", "SPDisplaysDataType"], text=True, timeout=10)
    except Exception:
        return []

    gpus = []
    current = None
    for line in output.splitlines():
        stripped = line.strip()
        if stripped.endswith(":") and not stripped.startswith(("Chipset Model", "Vendor", "VRAM", "Graphics/Displays")):
            if current:
                gpus.append(current)
            current = {"vendor": "Apple", "name": stripped.rstrip(":")}
        elif current and stripped.startswith("Chipset Model:"):
            current["name"] = stripped.split(":", 1)[1].strip()
        elif current and stripped.startswith("Vendor:"):
            current["vendor"] = stripped.split(":", 1)[1].strip()
        elif current and stripped.startswith("VRAM"):
            current["memory_total_text"] = stripped.split(":", 1)[1].strip()
    if current:
        gpus.append(current)
    return gpus


def get_video_card_info():
    sys_type = detect_video_system()
    if sys_type == "NVIDIA":
        return gather_nvidia_card_info()
    if sys_type == "AMD":
        return gather_amd_card_info()
    if sys_type == "Darwin":
        return gather_darwin_card_info()
    return []


def get_machine_info():
    return {
        "hostname": platform.node(),
        "system": platform.system(),
        "release": platform.release(),
        "cpu": get_cpu_info(),
        "memory": get_memory_info(),
        "gpus": get_video_card_info(),
        "collected_at": int(time.time()),
    }


if __name__ == "__main__":
    print(get_machine_info())
