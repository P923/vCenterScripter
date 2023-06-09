from enum import Enum
from vCenterScripter.common import *
from vCenterScripter.logger import Logger, print_


class Nic_Teaming(Enum):
    loadbalance_ip = "loadbalance_ip"
    loadbalance_srcmac = "loadbalance_srcmac"
    loadbalance_srcid = "loadbalance_srcid"
    failover_explicit = "failover_explicit"


def list_host_switches(host: vim.HostSystem) -> set:
    """
    List the virtual switches of a host
    :param host: Host
    :return a set of names of the host vswitches.
    """
    return list_host_objects(host.config.network.vswitch)


def get_host_switch(host: vim.HostSystem, name: str) -> vim.host.VirtualSwitch:
    """
    Get the virtual switch of a host
    :param name: of the vSwitch
    :param host: Host
    """
    return get_host_object(host.config.network.vswitch, name)


def add_host_switch(host: vim.HostSystem, name: str, num_ports: int, mtu:int, logger: Logger = None):
    """
    Create a new vSwitch on the host
    :param host:  Host
    :param name:  name of the new vSwitch
    :param num_ports: number of ports vSwitch
    :param mtu: MTU
    :param logger: Logger
    """
    vswitch_spec = vim.host.VirtualSwitch.Specification()
    vswitch_spec.numPorts = num_ports
    vswitch_spec.mtu = mtu
    host.configManager.networkSystem.AddVirtualSwitch(name, vswitch_spec)
    print_("Host: Added " + name + " vSwitch - (" + str(num_ports) + ":"+str(mtu)+")", logger)


def delete_host_switch(host: vim.HostSystem, name: str, logger: Logger = None):
    """
    Delete a virtual switch from a host
    :param host: Host where delete the virtual switch
    :param name: Name of the virtuaal sitch
    :param logger: Logger
    """
    host.configManager.networkSystem.RemoveVirtualSwitch(name)
    print_("Host: Deleted " + name + " vSwitch", logger)


def add_nic_switch(host: vim.HostSystem, switch:vim.host.VirtualSwitch, nic: vim.host.PhysicalNic, active = True):
    """
    Add a Nic to vSwitch
    :param host: Host
    :param switch: The Switch
    :param nic: Network Interface
    :param active: true for insert in Active, False for standby
    """
    host_config = next(x for x in host.config.network.vswitch if x.name == switch.name)
    nic_config = host_config.spec.policy.nicTeaming

    if active:
        nic_config.nicOrder.activeNic.append(nic.device)
    else:
        nic_config.nicOrder.standbyNic.append(nic.device)

    host_config.spec.bridge.nicDevice.append(nic.device)
    host.configManager.networkSystem.UpdateVirtualSwitch(switch.name, host_config.spec)


def remove_nic_switch(host: vim.HostSystem, switch:vim.host.VirtualSwitch, nic: vim.host.PhysicalNic):
    """
    Remove a Nic from vSwitch
    :param host: Host
    :param switch: The Switch
    :param nic: Network Interface
    """
    host_config = next(x for x in host.config.network.vswitch if x.name == switch.name)
    nic_config = host_config.spec.policy.nicTeaming

    if nic.device in nic_config.nicOrder.activeNic:
        nic_config.nicOrder.activeNic.remove(nic.device)

    if nic.device in nic_config.nicOrder.standbyNic:
        nic_config.nicOrder.standbyNic.remove(nic.device)

    if nic.device in host_config.spec.bridge.nicDevice:
        host_config.spec.bridge.nicDevice.remove(nic.device)

    host.configManager.networkSystem.UpdateVirtualSwitch(switch.name, host_config.spec)


def change_teaming_nic_switch(host: vim.HostSystem, switch:vim.host.VirtualSwitch, teaming: Nic_Teaming):
    """
    Change the teaming policy of a vSwitch
    :param host: Host
    :param switch: Virtual Switch
    :param teaming: check nic_teaming Enum.
    """
    host_config = next(x for x in host.config.network.vswitch if x.name == switch.name)
    nic_config = host_config.spec.policy.nicTeaming
    nic_config.policy = teaming.value
    host.configManager.networkSystem.UpdateVirtualSwitch(switch.name, host_config.spec)
