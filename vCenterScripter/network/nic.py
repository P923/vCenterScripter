from vCenterScripter.common import *


def list_host_nics(host: vim.HostSystem) -> set:
    """
    List the NICS of a host
    :param host: Host
    :return a set of names of the host Phisical NICs.
    """
    return list_host_objects(host.config.network.pnic)


def get_host_nic(host: vim.HostSystem, name: str) -> vim.host.PhysicalNic:
    """
    Get a Phisical Nic of a host
    :param name: of the vSwitch
    :param host: Host
    """
    return get_host_object(host.config.network.pnic, name)


