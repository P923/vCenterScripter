from pyVim.task import WaitForTask

from vCenterScripter.common import *


def list_folder_names(si: vim.ServiceInstance) -> set:
    """
    Get names of the Folders in the vCenter
    :param si: Connection to vCenter Server
    :return: Set of Folders names
    """
    return list_obj_names(si, vim.Folder)


def get_folder(si: vim.ServiceInstance, name: str = "") -> vim.Folder:
    """
    Get names of the Folders in the vCenter
    :param si: Connection to vCenter Server
    :param name: Name of the Folder (like Datacenter)
    :return: The Folder
    """
    return get_object(si, vim.Folder, name)


def create_folder(parent_folder: vim.Folder, folder_name: str):
    """
    Create a new Folder
    :param parent_folder: Parent folder
    :param folder_name: Name of the new folder
    :return the newly created folder
    """
    folder = parent_folder.CreateFolder(folder_name)
    return folder


def move_to_folder_vm(virtual_machine: vim.VirtualMachine, dest_folder: vim.Folder):
    """
    Move a VM to another folder   #TODO Test
    :param virtual_machine: the virtual Machine
    :param dest_folder: Destination folder
    """
    task = dest_folder.MoveIntoFolder_Task([virtual_machine])
    WaitForTask(task)
