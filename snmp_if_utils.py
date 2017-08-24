#!/usr/bin/env python

# Interface MIB
# http://www.oidview.com/mibs/0/IF-MIB.html

import datetime
import system_snmp

OPER_STATUS_MAP = {
    1: "up",
    2: "down",
    3: "testing",
    4: "unknown",
    5: "dormant",
    6: "notPresent",
    7: "lowerLayerDown",
    }

ADMIN_STATUS_MAP = {
    1: "up", 
    2: "down", 
    3: "testing",
    }

BGP_ADMIN_STATUS_MAP = {
    1: 'disabled',
    2: 'enabled',
    }

BGP_OPER_STATUS_MAP = {
    1: "idle",
    2: "connect",
    3: "active",
    4: "opensent",
    5: "openconfirm",
    6: "established",
    }

# List of dicts formatted as:
#   hostname: device_name (str)
#   if_table: if_table (dict)
# Used to cache if_table information to prevent repetetive if index lookups
DEVICE_LIST = list()


def __get_device_dict__(device):
    """ Private function to create a device dictionary if none exists or return
        an existing device dictionary

        Args:
            device (str)

        Returns:
            device_dict
    """

    device_dict = dict()

    # Verify device is not already present in our DEVICE_LIST
    for device_dict in DEVICE_LIST:
        if device == device_dict["hostname"]:
            return device_dict

    device_dict["hostname"] = device
    device_dict["if_table"] = get_if_table(device)

    DEVICE_LIST.append(device_dict)

    return device_dict
        


def __if_data__(device, oid, output_type, if_mib=None, override=None):
    """
    """
    if_dict = dict()
    device_dict = __get_device_dict__(device)
    
    if if_mib==None:
        snmp_data = system_snmp.snmp_bulkwalk(device, oid, override_flags=override)
        for if_tuple in snmp_data:
            if_dict[if_tuple[0].split(".")[-1]] = output_type(if_tuple[1])
        return if_dict

    else:
        if_tuple = system_snmp.snmp_get(device, "{}.{}".format(oid, if_mib), override_flags=override)
        if_dict[if_tuple[0].split(".")[-1]] = output_type(if_tuple[1])

        return if_dict


def get_if_table(device, inverse=False):
    """ Gets the interface table (if_index and interface) for a given device
        for further snmp lookups
        
        Args:
            device - devicename to get if table for (str)
        
        Returns:
            if_table - formatted as if_index:if (dict)
        
        OID: .1.3.6.1.2.1.2.2.1.2
    """
    
    if_table = dict()
    snmp_data = system_snmp.snmp_bulkwalk(device, ".1.3.6.1.2.1.2.2.1.2")
    
    for if_tuple in snmp_data:
        if inverse:
            if_table[if_tuple[1]] = if_tuple[0].split(".")[-1]
        else:
            if_table[if_tuple[0].split(".")[-1]] = if_tuple[1]
    
    return if_table


def get_if_desc(device, if_mib=None):
    """  Args:
            device (str)
            if_mib - interface mib (str)
        
        Returns:
            dict
        
        OID: .1.3.6.1.2.1.31.1.1.1.18
    """
    oid = ".1.3.6.1.2.1.31.1.1.1.18"
    return __if_data__(device, oid, str, if_mib)


def get_if_admin_status(device, if_mib=None):
    """ 
        OID: .1.3.6.1.2.1.2.2.1.7
    """
    oid = ".1.3.6.1.2.1.2.2.1.7"
    return {intf:ADMIN_STATUS_MAP[value] for intf,value in __if_data__(device, oid, int, if_mib).items()}


def get_if_oper_status(device, if_mib=None):
    """
        OID: .1.3.6.1.2.1.2.2.1.8
    """
    oid = ".1.3.6.1.2.1.2.2.1.8"
    return {intf:OPER_STATUS_MAP[value] for intf,value in __if_data__(device, oid, int, if_mib).items()}


def get_if_last_change(device, if_mib=None):
    """
        OID: .1.3.6.1.2.1.2.2.1.9
    """
    oid = ".1.3.6.1.2.1.2.2.1.9"
    return  __if_data__(device, oid, str, if_mib, override="-Oq")


def get_if_in_errors(device, if_mib=None):
    """
        OID: .1.3.6.1.2.1.2.2.1.14
    """
    oid = ".1.3.6.1.2.1.2.2.1.14"
    return __if_data__(device, oid, int, if_mib)


def get_if_out_errors(device, if_mib=None):
    """
        OID: 1.3.6.1.2.1.2.2.1.20
    """
    oid = ".1.3.6.1.2.1.2.2.1.20"
    return __if_data__(device, oid, int, if_mib)


def get_lldp_neighbors(device, if_mib=None):
    """
        OID:
    """
    oid = ""
    return __if_data__(device, oid, str, if_mib)


def get_bgp_asn(device):
    """
        OID: .1.3.6.1.2.1.15.2
    """
    oid= ".1.3.6.1.2.1.15.2"
    return system_snmp.snmp_bulkwalk(device, oid)[0]


def get_bgp_admin_status(device, peer_ip=None):
    """
        OID: .1.3.6.1.2.1.15.3.1.3.$v4_IP_ADDR
    """
    if peer_ip:
        oid = ".1.3.6.1.2.1.15.3.1.3.{}".format(peer_ip)
        return BGP_ADMIN_STATUS_MAP[system_snmp.snmp_get(device, oid)[1]]
    else:
        oid = ".1.3.6.1.2.1.15.3.1.3"
        return {".".join(peer_ip.split(".")[-4:]):BGP_ADMIN_STATUS_MAP[peer_state] for peer_ip,peer_state in system_snmp.snmp_bulkwalk(device, oid)}

def get_bgp_oper_status(device, peer_ip=None):
    """
        OID: .1.3.6.1.2.1.15.3.1.2.$v4_IP_ADDR
    """
    if peer_ip:
        oid = ".1.3.6.1.2.1.15.3.1.2.{}".format(peer_ip)
        return BGP_OPER_STATUS_MAP[system_snmp.snmp_get(device, oid)[1]]
    else:
        oid = ".1.3.6.1.2.1.15.3.1.2"
        return {".".join(peer_ip.split(".")[-4:]):BGP_OPER_STATUS_MAP[peer_state] for peer_ip,peer_state in system_snmp.snmp_bulkwalk(device, oid)}

