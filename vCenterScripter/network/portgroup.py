from vCenterScripter.common import *
from vCenterScripter.logger import Logger, print_


def list_host_portgroups(host: vim.HostSystem) -> set:
    """
    List the portgroup of a host
    :param host: Host
    :return a set of names of the host portgroups.
    """
    return list_host_objects(host.config.network.portgroup)


def get_host_portgroup(host: vim.HostSystem, name: str) -> vim.host.PortGroup:
    """
    Get the Portgroup of a host
    :param name: of the Portgroup
    :param host: Host
    """
    return get_host_object(host.config.network.portgroup, name)


def delete_host_portgroup(host: vim.HostSystem, name: str, logger: Logger = None):
    """
    Delete a PortGroup from a host
    :param host: Host where delete the pg
    :param name: Name of the pg
    :param logger: Logger
    """
    host.configManager.networkSystem.RemovePortGroup(name)

    print_("Host: Deleted " + name + " pg", logger)


def add_host_portgroup(host: vim.HostSystem,
                       switch:vim.host.VirtualSwitch,
                       portgroup_name:str,
                       vlan_id:int,
                       logger: Logger = None,
                       allowPromiscuous = True, macChanges = False, forgedTransmits = False):
    """
    Add a portgroup to Host
    :param logger:
    :param host: Host
    :param switch: Switch to add the portgroup
    :param portgroup_name: name of portgroup
    :param vlan_id: Vlan ID
    :param allowPromiscuous: allowPromiscuous
    :param macChanges: macChanges
    :param forgedTransmits: forgedTransmits
    :return:
    """
    portgroup_spec = vim.host.PortGroup.Specification()
    portgroup_spec.vswitchName = switch.name
    portgroup_spec.name = portgroup_name
    portgroup_spec.vlanId = int(vlan_id)
    network_policy = vim.host.NetworkPolicy()
    network_policy.security = vim.host.NetworkPolicy.SecurityPolicy()
    network_policy.security.allowPromiscuous = allowPromiscuous
    network_policy.security.macChanges = macChanges
    network_policy.security.forgedTransmits = forgedTransmits
    portgroup_spec.policy = network_policy

    host.configManager.networkSystem.AddPortGroup(portgroup_spec)
    print_("Added portgroup" + portgroup_name, logger)


def update_host_portgroup_vlan(host: vim.HostSystem,
                       portgroup: vim.host.PortGroup,
                       vlan_id: int,
                       logger: Logger = None):
    """
    Change the VLAN ID of a portgroup
    :param host: Host
    :param portgroup: Portgroup
    :param vlan_id: Vlan ID
    :param logger: Logger
    """
    spec = portgroup.spec
    spec.vlanId = int(vlan_id)
    host.configManager.networkSystem.UpdatePortGroup(pgName=portgroup.spec.name, portgrp=spec)
    print_("Modified portgroup " + portgroup.key, logger)


def update_host_portgroup_flags(host: vim.HostSystem,
                       portgroup: vim.host.PortGroup,
                       logger: Logger = None,
                        allowPromiscuous = True, macChanges = False, forgedTransmits = False):
    """
    Change flags of the portgroup
    :param host: Host
    :param portgroup: Portgroup
    :param logger: Logger
    :param allowPromiscuous: AllowPromiscuous
    :param macChanges: macChanges
    :param forgedTransmits: forgedTransmits
    """
    spec = portgroup.spec
    spec.policy.security.allowPromiscuous = allowPromiscuous
    spec.policy.security.macChanges = macChanges
    spec.policy.security.forgedTransmits = forgedTransmits
    host.configManager.networkSystem.UpdatePortGroup(pgName=portgroup.spec.name, portgrp=spec)
    print_("Modified portgroup " + portgroup.key, logger)
