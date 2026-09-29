from pathlib import Path

# from pathlib import Path

def read_text(path: Path):
    try:
        return path.read_text().strip()
    except (FileNotFoundError, PermissionError, OSError):
        return None
DRM = Path("/sys/class/drm")

cards = sorted(
    p for p in DRM.glob("card[0-9]*")
    if p.is_dir() and p.name[4:].isdigit()
)

for card in cards:
    print(card.name, "->", card.resolve())

# Resolve the PCI device

card = Path("/sys/class/drm/card0")
pci_device = (card / "device").resolve()

print(pci_device)
# /sys/devices/pci0000:00/0000:00:01.0/0000:01:00.0

# Read PCI identity

def pci_identity(card: Path):
    dev = (card / "device").resolve()

    return {
        "pci_address": dev.name,
        "vendor_id": read_text(dev / "vendor"),
        "device_id": read_text(dev / "device"),
        "subsystem_vendor_id": read_text(dev / "subsystem_vendor"),
        "subsystem_device_id": read_text(dev / "subsystem_device"),
        "class": read_text(dev / "class"),
        "revision": read_text(dev / "revision"),
        "modalias": read_text(dev / "modalias"),
        "boot_vga": read_text(dev / "boot_vga"),
        "numa_node": read_text(dev / "numa_node"),
    }

if __name__ == "__main__":
    # gpu_data = get_gpu_stats()
    pci_identity(card)
    # import json
    # print(json.dumps(gpu_data, indent=4))
