"""
Demo codes for https://stackoverflow.com/q/71461397/10909029
"""

from typing import Tuple, List
from socket import AF_LINK, AF_INET, AF_INET6

import psutil


class NetworkInterfaceNotFound(Exception):
    pass


def get_active_nets():
    """
    Get active NIC names.

    Returns:
        Set of active NIC names.
    """

    return {name for name, net in psutil.net_if_stats().items() if net.isup}


def determine_current_nic(*net_names) -> Tuple[str, str, List[str], List[str]]:
    """
    Determine primary active NIC.

    Notes:
        One NIC may have multiple addresses of same family. Thus returning in list.

    Args:
        *net_names: NIC names to look for. NIC priority == item order

    Returns:
        NIC's Name, MAC, IPv4 address list, IPv6 address list
    """

    types = {
        AF_LINK.name: [],
        AF_INET.name: [],
        AF_INET6.name: [],
    }

    active_nets = get_active_nets()
    address_dict = psutil.net_if_addrs()

    for net_name in net_names:

        if net_name in active_nets:
            # now we have the device.
            matching_name = net_name
            break

    else:
        # if none exists, raise
        raise NetworkInterfaceNotFound(f"There's no matching NIC with names {net_names}")

    for address in address_dict[matching_name]:
        types[address.family.name].append(address.address)

    return matching_name, types[AF_LINK.name][0], types[AF_INET.name], types[AF_INET6.name]
    # otherwise, no matching NIC


# ---

if __name__ == '__main__':
    name_, mac, ipv4, ipv6 = determine_current_nic("이더넷", "Wi-Fi", "Bluetooth 네트워크 연결")
    print(name_, mac, ipv4, ipv6)
