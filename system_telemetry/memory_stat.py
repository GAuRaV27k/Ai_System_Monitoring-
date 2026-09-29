import re
import subprocess
import psutil
import pprint
def get_ram_info():

    try:
        result = subprocess.run(
            ["sudo", "dmidecode", "-t", "17"],
            capture_output=True,
            text=True,
            check=True
        )

    except subprocess.CalledProcessError as e:
        print(f"dmidecode failed: {e}")
        return {
            "total_sticks": 0,
            "total_size_gib": 0,
            "modules": []
        }

    output = result.stdout

    # Split output into blocks.
    # Each installed/empty memory slot is represented by
    # a "Memory Device" block.
    blocks = re.split(r"\n\s*\n", output)

    modules = []

    for block in blocks:

        if "Memory Device" not in block:
            continue

        # Convert the block into key/value pairs
        data = {}

        for line in block.splitlines():

            match = re.match(r"^\s*([^:]+):\s*(.*)$", line)

            if match:
                key = match.group(1).strip()
                value = match.group(2).strip()

                data[key] = value

        # Ignore empty RAM slots
        size = data.get("Size")

        if not size or size.lower() == "no module installed":
            continue

        # Extract numeric size
        size_match = re.search(
            r"([\d.]+)\s*(GiB|GB|MiB|MB)",
            size,
            re.IGNORECASE
        )

        if not size_match:
            continue

        size_value = float(size_match.group(1))
        size_unit = size_match.group(2).lower()

        # Normalize everything to GiB
        if size_unit == "gib":
            size_gib = size_value

        elif size_unit == "gb":
            size_gib = size_value / 1.073741824

        elif size_unit == "mib":
            size_gib = size_value / 1024

        elif size_unit == "mb":
            size_gib = size_value / 1073.741824

        else:
            continue

        # Speed
        speed_match = re.search(
            r"(\d+)\s*MT/s",
            data.get("Speed", "")
        )

        speed_mt = (
            int(speed_match.group(1))
            if speed_match
            else None
        )

        module = {
            "size_gib": size_gib,
            "manufacturer": data.get("Manufacturer"),
            "type": data.get("Type"),
            "speed_mt": speed_mt,
            "form_factor": data.get("Form Factor"),
            "part_number": data.get("Part Number"),
            # "locator": data.get("Locator"),
            # "rank": data.get("Rank"),
            "configured_speed_mt": data.get(
                "Configured Memory Speed"
            ),
        }

        modules.append(module)

    total_size = sum(
        module["size_gib"]
        for module in modules
    )

    return {
        "total_sticks": len(modules),
        "total_size_gib": total_size,
        "modules": modules
    }
def memory_static():
    print(get_ram_info())
# print((memory_static()))
    

    
def memory_dynamic():
    physical_memory = psutil.virtual_memory()
    return {
        "Total": round(physical_memory.total / (1024 ** 3),4),
        "Used": round(physical_memory.active / (1024 ** 3),4),
        "Free": round(physical_memory.available / (1024 ** 3),4),
        "Cached" :round(physical_memory.cached / (1024 ** 3),4)
    }

# print(memory_dynamic())