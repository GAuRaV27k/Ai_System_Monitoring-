import psutil


# ========================== Dynamic ==========================

def network_dynamic():

    net_stat = psutil.net_io_counters()

    mib = 1024 * 1024

    return {
        "send_data_mib": round(net_stat.bytes_sent / mib, 2),
        "receive_data_mib": round(net_stat.bytes_recv / mib, 2),

        "packets_sent": net_stat.packets_sent,
        "packets_received": net_stat.packets_recv,

        # "send_errors": net_stat.errout,
        # "receive_errors": net_stat.errin,

        # "send_drops": net_stat.dropout,
        # "receive_drops": net_stat.dropin,
    }


# ========================== Static ==========================

def network_static():

    interfaces = psutil.net_if_addrs()
    interface_stats = psutil.net_if_stats()

    networks = {}

    def _fam_name(fam):
        # Map common families to short names
        try:
            name = str(fam)
        except Exception:
            name = repr(fam)
        # psutil/family may be int or enum; normalize common ones
        if getattr(fam, "name", None):
            name = fam.name
        else:
            if name.endswith("AF_INET") or name == "AddressFamily.AF_INET":
                name = "IPv4"
            elif name.endswith("AF_INET6") or name == "AddressFamily.AF_INET6":
                name = "IPv6"
            elif name.endswith("AF_PACKET") or name == "AddressFamily.AF_PACKET":
                name = "MAC"
        return name

    for interface, addresses in interfaces.items():
        stats = interface_stats.get(interface)

        # Minimal output: is_up, speed_mbps, mtu, and simple addresses list
        networks[interface] = {
            "is_up": bool(stats.isup) if stats else None,
            "speed_mbps": int(stats.speed) if stats and stats.speed is not None else None,
            "mtu": int(stats.mtu) if stats and stats.mtu is not None else None,
            "addresses": [
                {
                    "type": _fam_name(address.family),
                    "address": address.address,
                }
                for address in addresses
            ],
        }

    return networks


# ========================== Test ==========================

# if __name__ == "__main__":

#     print("=== NETWORK STATIC ===")
#     print(network_static())

#     print("\n=== NETWORK DYNAMIC ===")
#     print(network_dynamic())