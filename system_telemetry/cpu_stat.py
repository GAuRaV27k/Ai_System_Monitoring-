import platform # for the cpu information 

import psutil  # for the system information 
# ==========================helper functions =====================================



def get_cpu_name():

    # Fallback to platform module for Windows/macOS compatibility
    if platform.system() != "Linux":
        return platform.processor()
    
    # Linux-specific handling
    try:
        with open("/proc/cpuinfo", "r") as f:
            for line in f:
                if "model name" in line:
                    # Strip out the label and return the actual CPU name
                    return line.split(":")[1].strip()
    except Exception:
        pass
    
    return "Unknown Processor"

# ========================== End helper functions =====================================
def cpu_static():
    freq = psutil.cpu_freq()
    return {
        "processor": get_cpu_name(),
        "architecture": platform.machine(),
        "physical_cores": psutil.cpu_count(logical=False),
        "logical_cores": psutil.cpu_count(logical=True),
        "minimum_cpu_frequency" : freq.max,
        "maximum_cpu_frequency" : freq.min,
    }

# print(cpu_static())

def cpu_dynamic():

    cpu_times = psutil.cpu_times()

    return {
        "user_active": round(cpu_times.user / 3600, 2),
        "idle_active": round(cpu_times.idle / 3600, 2),
        "system_active": round(cpu_times.system / 3600, 2),
        "cpu_current_utilization": psutil.cpu_percent(),
    }
def cpu_load():
    return psutil.getloadavg()

# print("cpu load :",cpu_load())
# 
# print(cpu_dynamic())

