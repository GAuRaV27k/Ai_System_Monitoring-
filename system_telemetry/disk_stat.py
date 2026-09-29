import os

import psutil


def get_disk_info_sysfs():
    """Return metadata for real block devices under /sys/block."""
    sys_block = "/sys/block"
    if not os.path.isdir(sys_block):
        return []

    devices = []
    for disk in sorted(os.listdir(sys_block)):
        if disk.startswith(("loop", "ram", "zram", "dm-")):
            continue

        info = {
            "name": disk,
            "device": f"/dev/{disk}",
        }

        model_path = os.path.join(sys_block, disk, "device", "model")
        if os.path.exists(model_path):
            try:
                with open(model_path, "r", encoding="utf-8", errors="replace") as f:
                    info["model"] = f.read().strip() or None
            except OSError:
                pass

        vendor_path = os.path.join(sys_block, disk, "device", "vendor")
        if os.path.exists(vendor_path):
            try:
                with open(vendor_path, "r", encoding="utf-8", errors="replace") as f:
                    info["manufacturer"] = f.read().strip() or None
            except OSError:
                pass

        rot_path = os.path.join(sys_block, disk, "queue", "rotational")
        if os.path.exists(rot_path):
            try:
                with open(rot_path, "r", encoding="utf-8", errors="replace") as f:
                    rotational = f.read().strip()
                    if rotational == "1":
                        info["type"] = "HDD"
                    elif rotational == "0":
                        info["type"] = "SSD/NVMe"
            except OSError:
                pass

        if not info.get("model") and not info.get("manufacturer") and info.get("type") is None:
            if not os.path.exists(os.path.join(sys_block, disk, "device")):
                continue

        # Remove unset fields for a minimal output.
        info = {key: value for key, value in info.items() if value is not None and value != "unknown"}

        devices.append(info)

    return devices


def disk_static():
    partition_stats = []

    for part in psutil.disk_partitions(all=True):
        if not part.device.startswith("/dev/"):
            continue
        try:
            usage = psutil.disk_usage(part.mountpoint)
        except (OSError, PermissionError):
            continue

        partition_stats.append(
            {
                "device": part.device,
                "mountpoint": part.mountpoint,
                "fstype": part.fstype,
                "size_gb": round(usage.total / (1024 ** 3), 3),
                "used_gb": round(usage.used / (1024 ** 3), 3),
                "free_gb": round(usage.free / (1024 ** 3), 3),
                "percent": round(usage.percent, 3),
            }
        )

    return {
        "Disks": get_disk_info_sysfs(),
        "partitions": partition_stats,
    }

