# GPU System Reference

This document records the GPU topology and telemetry that the monitoring code can safely collect. It omits one-time readings, exhaustive sysfs listings, duplicated tables, and example output.

## Detected GPUs

| Role | DRM card | Render node | PCI address | Model | Driver |
| --- | --- | --- | --- | --- | --- |
| Dedicated | card0 | renderD129 | 0000:01:00.0 | NVIDIA AD107M GeForce RTX 4050 Max-Q / Mobile | nouveau |
| Integrated | card1 | renderD128 | 0000:00:02.0 | Intel Raptor Lake-S UHD Graphics | i915 |

- The Intel GPU is the boot display adapter (boot_vga=1) and drives the internal eDP-1 display.
- The NVIDIA GPU is connected through the Intel PCIe bridge at 0000:00:01.0.
- Use the PCI address as the persistent GPU ID. DRM card and render-node numbering can change between boots.

## Safe Generic Data

Read the following from each DRM card resolved device path:

| Data | Path | Notes |
| --- | --- | --- |
| PCI identity | vendor, device, subsystem_vendor, subsystem_device, class, revision | Stable hardware metadata |
| Driver | driver symlink | Resolve the symlink name |
| Boot adapter | boot_vga | Useful for display-role detection |
| Runtime power | power_state, power/runtime_status | PCI and runtime-PM state only |
| PCIe link | current_link_speed, current_link_width | Available where the platform exposes it |
| Display connectors | /sys/class/drm/cardN-*/ | Read status, enabled, modes, and edid |

Connector entries describe displays attached to a card; they are not additional GPUs. EDID is binary and must be read as bytes.

## Available Vendor Telemetry

### Intel (i915)

The Intel card exposes these optional files when present:

- Frequency: gt_cur_freq_mhz, gt_act_freq_mhz, gt_min_freq_mhz, gt_max_freq_mhz, and gt_boost_freq_mhz
- GT details: gt/gt0/rps_* and gt/gt0/throttle_reason_*
- Power residency: power/rc6_enable and power/rc6_residency_ms
- Engine metadata: engine/*/{name,class,instance,capabilities}

No standard sysfs gpu_busy_percent file is available on this system.

### NVIDIA (nouveau)

The observed nouveau sysfs tree provides GPU identity, DRM connectors, and PCI/runtime-power state. It does not provide usable utilization, temperature, VRAM, clocks, fan speed, or power telemetry.

For detailed NVIDIA data, use NVML through the proprietary NVIDIA driver when it is installed and available.

## Unavailable Fields

Do not report unavailable data as zero. Return None, omit the field, or include an availability state for:

- GPU utilization and per-engine busy percentage
- GPU temperature, power usage, fan speed, voltage, and power limit
- VRAM total, used, and free
- NVIDIA clocks, throttle reasons, and firmware details

Existing system thermal zones and generic hwmon entries are not associated with either GPU, so they must not be labeled as GPU temperature.

## Collection Rules

1. Enumerate /sys/class/drm/card[0-9]* directories.
2. Resolve card/device, then retain devices whose PCI class begins with 0x03.
3. Read PCI identity and driver information.
4. Associate the card with render nodes and connector directories.
5. Collect generic DRM and PCI data.
6. Select optional telemetry by vendor ID and driver:
   - 0x8086 with i915 or xe: Intel backend
   - 0x1002 with amdgpu: AMD backend
   - 0x10de with nvidia: NVML backend when available
   - 0x10de with nouveau: generic DRM/PCI data only

Only read sysfs files. Never write control files such as remove, rescan, reset, enable, driver_override, bind, or unbind.

## Recommended Output Fields

Store at least:

    pci_address
    vendor_id
    device_id
    subsystem_vendor_id
    subsystem_device_id
    driver
    drm_card
    render_node
    connectors
    power_state
    runtime_status

Add vendor-specific fields only after confirming that the corresponding file or API is available.
