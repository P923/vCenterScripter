
from vCenterScripter.common import *
from vCenterScripter.logger import Logger, print_


def list_host(si: vim.ServiceInstance) -> set:
    """
    Get names of the Host in the vCenter
    :param si: Connection to vCenter Server
    :return: Set of Host names
    """
    return list_obj_names(si, vim.HostSystem)


def get_host(si: vim.ServiceInstance, name: str = "") -> vim.HostSystem:
    """
    Get the 'name' Host
    :param si: Connection to vCenter Server
    :param name: Name of the VM  (for example 192.168.0.201)
    :return: Virtual Machine
    """
    return get_object(si, vim.HostSystem, name)


def refresh_host(si: vim.ServiceInstance, host: vim.HostSystem) -> vim.HostSystem:
    """
    Refresh the Host after a destructive operation
    :param si: Connection to vCenter
    :param host: The Host to be refreshed
    :return: The new Host
    """
    name = host.config.name
    del host
    return get_host(si, name)


def enter_maintenance(host: vim.HostSystem, logger: Logger = None):
    """
    Put in Maintenance mode a host
    :param host: HostSystem
    :param logger: Logger
    :return:
    """
    host.EnterMaintenanceMode(0)
    print_("Host: entering maintenance mode.", logger)


def exit_maintenance(host: vim.HostSystem,  logger: Logger = None):
    """
    Put in Maintenance mode a host
    :param host: HostSystem
    :param logger: Logger
    :return:
    """
    host.ExitMaintenanceMode(0)
    print_("Host: exiting maintenance mode.", logger)


def list_resource_pool_host(si: vim.ServiceInstance, host: vim.HostSystem) -> set:
    """
    Get names of the Resource Pools of a specific HostSystem.
    :param host: Host
    :param si: Connection to the vCenter.
    :return: a set of names of Resource pools where the host is present
    """
    resources = list_obj(si, vim.ResourcePool)
    set_names = set([pool.name for pool in resources if pool.owner.name == host.summary.config.name])
    return set_names


def get_resource_pool_host(si: vim.ServiceInstance, host: vim.HostSystem, name: str ="") -> vim.ResourcePool:
    """
    Get the "Name" resource pool of a specific HostSystem.
    :param si: Connection to the vCenter
    :param host: Host
    :param name: Name of the Resource Pool. Standard "Resources"
    :return: a resource pool
    """
    resources = list_obj(si, vim.ResourcePool)
    resource_pool = next((pool for pool in resources if pool.owner.name == host.summary.config.name and pool.name == name), None)
    return resource_pool


