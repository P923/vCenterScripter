from vCenterScripter.common import *
from vCenterScripter.logger import Logger, print_


def list_host_vnics(host: vim.HostSystem) -> set:
    """
    List the VNICS of a host
    :param host: Host
    :return a set of names of the host  VNICs.
    """
    return list_host_objects(host.config.network.vnic)


def get_host_nic(host: vim.HostSystem, name: str) -> vim.host.VirtualNic:
    """
    Get a VNic of a host
    :param name: of the vSwitch
    :param host: Host
    """
    return get_host_object(host.config.network.vnic, name)


def add_host_vmnic_ip(host: vim.HostSystem, portgroup: vim.host.PortGroup, mtu: int, ip: vim.host.IpConfig, logger: Logger = None):
    """
    Add a VNic to a portgroup of a Host
    :param host: Host
    :param portgroup: Portgroup
    :param mtu: MTU
    :param ip: Fixed IP
    :param logger: Logger
    """
    vnic_config = vim.host.VirtualNic.Specification()
    vnic_config.mtu = mtu
    vnic_config.ip = ip
    _ = host.configManager.networkSystem.AddVirtualNic(
        portgroup,
        vnic_config
    )
    print_("vmnic added!", logger)


def delete_host_vmnic(host: vim.HostSystem, vnic: vim.host.VirtualNic, logger: Logger = None):
    host.configManager.networkSystem.RemoveVirtualNic(vnic)
    print_("vminc deleted!", logger)


def get_dict_services() -> dict:
    """
    :return: A dict with all the services that can be enabled in a VMKernel NIC.
    """
    dict = {
    "vMotion":"deselect",
    "Provisioning":"deselect",
    "Fault tolerance logging":"deselect",
    "Management":"deselect",
    "Replication":"deselect",
    "NFC replication":"deselect"}
    return dict


class vnic_services:
    """
    Class to help with the Select/Deselect of the services that can be enabled in a VMKernel NIC.
    """
    def __init__(self, services):
        self.services = services

