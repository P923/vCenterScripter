from pyvim.task import WaitForTask
from pyVmomi import vim

from vCenterScripter.common import list_obj_names, get_object
from vCenterScripter.logger import Logger, print_
from vCenterScripter.vm import refresh_vm


def generate_snapshot(conn: vim.ServiceInstance, vm: vim.VirtualMachine, name: str, desc: str = "", logger: Logger = None,
                      quiesce: bool = False, memory: bool = False) -> vim.VirtualMachine:
    """
    Generate a snapshot for a VM
    :param conn: To refresh VM once executed the operation
    :param vm: Virtual Machine
    :param logger: Logger
    :param name: Name of snapshot
    :param desc: Description of the snapshot
    :param quiesce: Quiesce
    :param memory: Memory
    :return: Virtual Machine refreshed
    """
    WaitForTask(vm.CreateSnapshot_Task(name=name,
                                       description=desc,
                                       memory=memory,
                                       quiesce=quiesce))
    print_("Snapshot %s generated" % name, logger)
    return refresh_vm(conn, vm)


def delete_revert_snapshot(conn: vim.ServiceInstance, vm: vim.VirtualMachine, name: str,
                           delete: bool, logger: Logger = None) -> vim.VirtualMachine:
    """
    Delete or revert a snapshot
    :param conn: To refresh VM once executed the operation
    :param vm: Virtual Machine
    :param name: Name of the snapshot to revert or to be removed
    :param delete: True for deletion, False for revert
    :param logger: Logger
    :return: Virtual Machine refreshed
    """
    snap_obj = get_snapshots_by_name_recursively(vm.snapshot.rootSnapshotList, name)
    if len(snap_obj) == 1:
        snap_obj = snap_obj[0].snapshot
        if delete:
            print_("Removing snapshot %s" % name, logger)
            WaitForTask(snap_obj.RemoveSnapshot_Task(True))
        else:
            print_("Reverting to snapshot %s" % name, logger)
            WaitForTask(snap_obj.RevertToSnapshot_Task())
    else:
        print_("No snapshots found with name: %s on VM: %s" % (
            name, vm.name), logger)

    return refresh_vm(conn, vm)


def get_snapshots_by_name_recursively(snapshots, snapname: str):
    """"""
    snap_obj = []
    for snapshot in snapshots:
        if snapshot.name == snapname:
            snap_obj.append(snapshot)
        else:
            snap_obj = snap_obj + get_snapshots_by_name_recursively(
                snapshot.childSnapshotList, snapname)
    return snap_obj


def list_datastores(si: vim.ServiceInstance) -> set:
    """
    Get names of the Datastores in the vCenter
    :param si: Connection to vCenter Server
    :return: Set of Datastores names
    """
    return list_obj_names(si, vim.Datastore)


def get_datastore(si: vim.ServiceInstance, name: str = "") -> vim.Datastore:
    """
    Get a Datastore in the vCenter
    :param name: Name of the Datstore
    :param si: Connection to vCenter Server
    :return: The Name Datstore
    """
    return get_object(si, vim.Datastore, name)

# TODO Add - Remove a Datastore