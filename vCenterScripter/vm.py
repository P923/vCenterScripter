import re
import time
from typing import List

from pyvim.task import WaitForTask

from vCenterScripter.common import *
from vCenterScripter.logger import Logger, print_


def list_vm_names(si: vim.ServiceInstance) -> set:
    """
    Get names of the VMs in the vCenter
    :param si: Connection to vCenter Server
    :return: Set of Virtual Machines names
    """
    return list_obj_names(si, vim.VirtualMachine)


def refresh_vm(si: vim.ServiceInstance, vm: vim.VirtualMachine) -> vim.VirtualMachine:
    """
    Refresh the vm after a destructive operation
    :param si: Connection to vCenter
    :param vm: The VM to be refreshed
    :return: The new VM
    """
    name = vm.config.name
    del vm
    return get_vm(si, name)


def get_vm(si: vim.ServiceInstance, name: str = "") -> vim.VirtualMachine:
    """
    Get the 'name' VM
    :param si: Connection to vCenter Server
    :param name: Name of the VM
    :return: Virtual Machine
    """
    return get_object(si, vim.VirtualMachine, name)


def check_vmware_tools(virtual_machine: vim.VirtualMachine, logger: Logger = None, blocking=False):
    """
    Check if in the VM is installed Vmware Tools
    :param virtual_machine: The virtual Machine
    :param logger: Logger
    :param blocking: if blocking = True, exit the program
    :return: True or False
    """
    tools_status = virtual_machine.guest.toolsStatus
    if tools_status in ('toolsNotInstalled', 'toolsNotRunning'):
        print_(
            "VMwareTools is either not running or not installed. "
            "Rerun the script after verifying that VMwareTools "
            "is running", logger)
        if blocking:
            exit(-1)
        return False
    return True


def run_program(si: vim.ServiceInstance,
                virtual_machine: vim.VirtualMachine,
                credentials: vim.vm.guest.NamePasswordAuthentication,
                program_path: str,
                logger: Logger = None,
                program_arguments: str = None,
                working_directory: str = "",
                envVariables=None,
                async_run: bool = False):
    """
    Run a program inside the VM using VMWare tools
    :param si: Connection to Vcenter
    :param virtual_machine: The virtual Machine
    :param credentials: The credentials of the VM
    :param program_path: Path of the program to run
    :param logger: Logger
    :param program_arguments: Program Arguments if needed
    :param async_run: True if you want it non-blocking
    :param working_directory: Where to run the program
    :param envVariables: Environment Variables.
    :return: The PID of the process.
    """

    check_vmware_tools(virtual_machine, logger, blocking=True)
    content = si.RetrieveContent()
    profile_manager = content.guestOperationsManager.processManager

    if program_arguments:
        program_spec = vim.vm.guest.ProcessManager.ProgramSpec(
            envVariables=envVariables,
            workingDirectory=working_directory,
            programPath=program_path,
            arguments=program_arguments)

    else:
        program_spec = vim.vm.guest.ProcessManager.ProgramSpec(
            envVariables=envVariables,
            workingDirectory=working_directory,
            programPath=program_path)

    res = profile_manager.StartProgramInGuest(virtual_machine, credentials, program_spec)

    if res > 0:
        print_("Program submitted, PID is %d" % res, logger)
        pid_exitcode = \
            profile_manager.ListProcessesInGuest(virtual_machine, credentials, [res]).pop().exitCode

        if not async_run:
            while re.match('[^0-9]+', str(pid_exitcode)):
                print_("Program running,   PID is %d" % res, logger)
                time.sleep(5)
                pid_exitcode = \
                    profile_manager.ListProcessesInGuest(virtual_machine, credentials, [res]).pop().exitCode
                if pid_exitcode == 0:
                    print_("Program %d completed with success" % res, logger)
                    break
                elif re.match('[1-9]+', str(pid_exitcode)):
                    print_("ERROR: Program %d completed with Failure" % res, logger)
                    print_("  tip: Try running this on guest %r to debug"
                           % virtual_machine.summary.guest.ipAddress, logger)
                    print_("ERROR: More info on process", logger)
                    print_(profile_manager.ListProcessesInGuest(virtual_machine, credentials, [res]), logger)
                    break

    return res


def terminate_pid(pid: int,
                  si: vim.ServiceInstance,
                  virtual_machine: vim.VirtualMachine,
                  credentials: vim.vm.guest.NamePasswordAuthentication,
                  logger: Logger = None,
                  ):
    """
    Terminate a PID inside the VM using VMWare tools
    :param pid: Pid of the process to be killed
    :param si: Connection to Vcenter
    :param virtual_machine: The virtual Machine
    :param credentials: The credentials of the VM
    :param logger: Logger
    """
    check_vmware_tools(virtual_machine, logger, blocking=True)
    content = si.RetrieveContent()
    profile_manager = content.guestOperationsManager.processManager
    profile_manager.TerminateProcessInGuest(virtual_machine, credentials, pid)


def get_info_pid(
        pid: int,
        si: vim.ServiceInstance,
        virtual_machine: vim.VirtualMachine,
        credentials: vim.vm.guest.NamePasswordAuthentication,
        logger: Logger = None,
) -> vim.vm.guest.ProcessManager.ProcessInfo:
    """
    Get info about the PID process, using VMware Tools
    :param pid: Pid of the process
    :param si: Connection to Vcenter
    :param virtual_machine: The virtual Machine
    :param credentials: The credentials of the VM
    :param logger: Logger
    :return: Info about the selected PID or None.
    """
    check_vmware_tools(virtual_machine, logger, blocking=True)
    content = si.RetrieveContent()
    profile_manager = content.guestOperationsManager.processManager
    return profile_manager.ListProcessesInGuest(virtual_machine, credentials, [pid]).pop()


def get_info_processes(si: vim.ServiceInstance,
                       virtual_machine: vim.VirtualMachine,
                       credentials: vim.vm.guest.NamePasswordAuthentication,
                       logger: Logger = None,
                       ) -> List[vim.vm.guest.ProcessManager.ProcessInfo]:
    """
    Get a list of processes running inside the Virtual Machine
    :param si: Connection to Vcenter
    :param virtual_machine: The virtual Machine
    :param credentials: The credentials of the VM
    :param logger: Logger
    :return: a list of info of processes
    """

    check_vmware_tools(virtual_machine, logger, blocking=True)
    content = si.RetrieveContent()
    profile_manager = content.guestOperationsManager.processManager
    processes = profile_manager.ListProcessesInGuest(virtual_machine, credentials, [])
    return processes


def relocate_vm(virtual_machine: vim.VirtualMachine,
                logger: Logger = None,
                dest_host: vim.HostSystem = None,
                dest_pool: vim.ResourcePool = None,
                dest_datastore: vim.Datastore = None):
    """
    Relocate a VM in a new host
    :param virtual_machine: VM to be relocated
    :param logger: logger
    :param dest_host: Destination host for the VM
    :param dest_pool: Destination Pool for the VM
    :param dest_datastore: Datastore to migrate the disk to. (moveAllDiskBackingsAndDisallowSharing)

    Check https://vdc-repo.vmware.com/vmwb-repository/dcr-public/1ef6c336-7bef-477d-b9bb-caa1767d7e30/82521f49-9d9a-42b7-b19b-9e6cd9b30db1/vim.vm.RelocateSpec.html
    For the correct params.
    """

    relocate_spec = vim.vm.RelocateSpec(host=dest_host, datastore=dest_datastore, pool=dest_pool)
    virtual_machine.Relocate(relocate_spec)
    print_("VM:" + virtual_machine.name + " relocated.", logger)


def power_off_vm(virtual_machine: vim.VirtualMachine,
                 logger: Logger = None):
    """
    Power off a VM
    :param virtual_machine: The VM
    :param logger: Logger
    """
    WaitForTask(virtual_machine.PowerOffVM_Task())
    print_("VM" + virtual_machine.name + "Powered off", logger)


def power_on_vm(virtual_machine: vim.VirtualMachine,
                logger: Logger = None,
                host: vim.HostSystem = None):
    """
    Power on a VM
    :param virtual_machine: The VM
    :param logger: Logger
    :param host The host were to power on the machine. None if were is registered
    """
    if host is not None:
        WaitForTask(virtual_machine.PowerOnVM_Task(host))
    else:
        WaitForTask(virtual_machine.PowerOnVM_Task())

    print_("VM " + virtual_machine.name + "Powered on.", logger)


def reload_vm(virtual_machine: vim.VirtualMachine, datastore_path: str,
              logger: Logger = None):
    """
    Unregister and register a VM on the same Head
    :param datastore_path: The path of the VM on the Datastore
    :param virtual_machine: The VM
    :param logger: Logger
    """
    WaitForTask(virtual_machine.reloadVirtualMachineFromPath_Task(datastore_path))
    print_("VM " + virtual_machine.name + "reloaded.", logger)


def unregister_vm(virtual_machine: vim.VirtualMachine,
                  logger: Logger = None):
    """
    Unregister on a VM.
    :param virtual_machine: The VM.
    :param logger: Logger
    """

    virtual_machine.UnregisterVM()
    print_("VM " + virtual_machine.name + "unregistered.", logger)


def register_vm(si: vim.ServiceInstance,
                folder: vim.Folder,
                datastore_path: str,
                name_vm: str,
                dest_host: vim.HostSystem,
                dest_pool: vim.ResourcePool,
                as_Template: bool = False,
                logger: Logger = None):
    """
    Register a VM to a host
    :param si: Connection to the vCenter
    :param folder: folder of Destination
    :param datastore_path: Path to the VM Disk
    :param name_vm: Name of the VM
    :param dest_host: Destination host for the VM
    :param dest_pool: Destination Pool for the VM
    :param as_Template: True if it is a template
    :param logger: Logger
    """

    # TODO Check if path is accessible from the host
    vms = list_obj(si, vim.VirtualMachine)
    for vm in vms:
        if vm.summary.config.vmPathName == datastore_path and vm.summary.runtime.connectionState == 'orphaned':
            try:
                unregister_vm(vm, logger)
            except Exception:
                pass

    WaitForTask(folder.RegisterVM_Task(path=datastore_path, name=name_vm, asTemplate=as_Template, host=dest_host,
                                       pool=dest_pool))
    print_("VM " + datastore_path + "registered.", logger)


def get_config_info_vm(virtual_machine: vim.VirtualMachine) -> vim.vm.ConfigInfo:
    """
    Get the configuration of a vm
    :param virtual_machine:
    :return the configuration of the VM.
    """
    return virtual_machine.config


def reconfig_spec_vm(virtual_machine: vim.VirtualMachine, name: str = None,
                     num_cpus: int = None, num_cores_per_socket: int = None,
                     memory_gb: int = None,
                     cpu_hot_add_enabled: bool = None, memory_hot_add_enabled: bool = None,
                     annotation: str = None):
    """
    Reconfig the specs of a VM
    :param memory_hot_add_enabled: Whether memory can be added to the virtual machine while it is running. This attribute can only be set when the virtual machine is powered-off
    :param name: Display name of the virtual machine
    :param num_cpus:  Number of virtual processors in a virtual machine
    :param num_cores_per_socket: Number of cores among which to distribute CPUs in this virtual machine
    :param memory_gb: Size of a virtual machine's memory, in GB
    :param cpu_hot_add_enabled: Whether virtual processors can be added to the virtual machine while it is running
    :param virtual_machine: The Virtual Machine
    :param annotation:  User-provided description of the virtual machine

    """
    config = vim.vm.ConfigSpec()
    if name is not None:
        config.name = name
    if num_cpus is not None:
        config.numCPUs = num_cpus
    if num_cores_per_socket is not None:
        config.numCoresPerSocket = num_cores_per_socket
    if memory_gb is not None:
        config.memoryMB = memory_gb * 1024
    if cpu_hot_add_enabled is not None:
        config.cpuHotRemoveEnabled = cpu_hot_add_enabled
    if memory_hot_add_enabled is not None:
        config.memoryHotAddEnabled = memory_hot_add_enabled
    if annotation is not None:
        config.annotation = annotation

    virtual_machine.ReconfigVM_Task(config)


def get_names_disk_vm(virtual_machine: vim.VirtualMachine) -> set:
    """
    Get all names of Hard Disk of a specific VM
    :param virtual_machine: The Virtual Machine
    :return: A set of Hard disk Names of a specific VM
    """
    names = set(device.deviceInfo.label for device in virtual_machine.config.hardware.device if
                hasattr(device.backing, 'fileName'))
    return names


def resize_disk_vm(virtual_machine: vim.VirtualMachine, disk_name: str, disk_size_gb: int):
    """
    Resize the disk of a VM
    :param disk_name: The name of the disk
    :param virtual_machine: Virtual Machine
    :param disk_size_gb: size in GB
    """

    disk = None
    for device in virtual_machine.config.hardware.device:
        if hasattr(device.backing, 'fileName') and device.deviceInfo.label == disk_name:
            disk = device

    if disk is not None:
        disk_spec = vim.vm.device.VirtualDeviceSpec()
        disk_mod = vim.vm.device.VirtualDisk()

        disk_mod.controllerKey = disk.controllerKey
        disk_mod.unitNumber = disk.unitNumber
        disk_mod.backing = disk.backing
        disk_mod.key = disk.key
        disk_mod.capacityInKB = disk_size_gb * 1024 * 1024

        disk_spec.device = disk_mod
        disk_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.edit

        dev_changes = []
        spec = vim.vm.ConfigSpec()
        dev_changes.append(disk_spec)
        spec.deviceChange = dev_changes
        WaitForTask(virtual_machine.ReconfigVM_Task(spec=spec))


def remove_disk_vm(virtual_machine: vim.VirtualMachine, disk_name: str, delete_disk: bool = False):
    """
    Remove a disk from a VM
    :param disk_name: The name of the disk
    :param virtual_machine: Virtual Machine
    :param delete_disk: True if you want also to delete it from the Datastore
    """

    disk = None
    for device in virtual_machine.config.hardware.device:
        if hasattr(device.backing, 'fileName') and device.deviceInfo.label == disk_name:
            disk = device

    if disk is not None:
        disk_spec = vim.vm.device.VirtualDeviceSpec()
        disk_spec.device = disk
        # Action on the VM -> Remove the Disk
        disk_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.remove
        if delete_disk:
            # Action on the Disk -> Delete File
            disk_spec.fileOperation = vim.vm.device.VirtualDeviceSpec.FileOperation.destroy

        dev_changes = []
        spec = vim.vm.ConfigSpec()
        dev_changes.append(disk_spec)
        spec.deviceChange = dev_changes
        WaitForTask(virtual_machine.ReconfigVM_Task(spec=spec))


def add_disk_to_vm(virtual_machine: vim.VirtualMachine, disk_size_gb: int):
    """
    Add a disk to a VM of size disk_size_mb
    :param virtual_machine: Virtual Machine
    :param disk_size_gb: size in GB
    """
    spec = vim.vm.ConfigSpec()

    # Get all disks on a VM, set unit_number to the next available
    unit_number = 0
    controller = None
    for device in virtual_machine.config.hardware.device:
        if hasattr(device.backing, 'fileName'):
            unit_number = int(device.unitNumber) + 1
            # unit_number 7 reserved for scsi controller
            if unit_number == 7:
                unit_number += 1
            if unit_number >= 16:
                print("we don't support this many disks")
                return -1
        if isinstance(device, vim.vm.device.VirtualSCSIController):
            controller = device
    if controller is None:
        print("Disk SCSI controller not found!")
        return -1

    # Prepare to add the disk to the VM
    dev_changes = []
    new_disk_kb = int(disk_size_gb) * 1024 * 1024
    disk_spec = vim.vm.device.VirtualDeviceSpec()
    disk_spec.fileOperation = vim.vm.device.VirtualDeviceSpec.FileOperation.create  # Action on the datastore -> Create the Disk
    disk_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add  # Action on the VM -> Add the Disk
    disk_spec.device = vim.vm.device.VirtualDisk()
    disk_spec.device.backing = vim.vm.device.VirtualDisk.FlatVer2BackingInfo()
    disk_spec.device.backing.diskMode = 'persistent'
    disk_spec.device.unitNumber = unit_number
    disk_spec.device.capacityInKB = new_disk_kb
    disk_spec.device.controllerKey = controller.key
    dev_changes.append(disk_spec)
    spec.deviceChange = dev_changes

    WaitForTask(virtual_machine.ReconfigVM_Task(spec=spec))
    print("%sGB disk added to %s" % (disk_size_gb, virtual_machine.config.name))


def destroy_vm(virtual_machine: vim.VirtualMachine):
    """
    Destroy a VM
    """
    virtual_machine.Destroy_Task()


def clone_vm(virtual_machine: vim.VirtualMachine,
             datastore: vim.Datastore,
             folder:vim.Folder,
             dest_host: vim.HostSystem,
             dest_pool: vim.ResourcePool,
             name: str,
             num_cpus: int, num_cores_per_socket: int,
             memory_gb: int
            ):
    """
    Clone a VM. #TODO Test
    :param virtual_machine: Virtual Machine to be cloned.
    :param datastore: Datastore of destination.
    :param folder: Folder of destination.
    :param dest_host: Host of destination.
    :param dest_pool: Pool of destination.
    :param name: Name of VM.
    :param num_cpus: Number of CPUs.
    :param num_cores_per_socket: Number of cores for socket.
    :param memory_gb: GB of RAM Memory.
    """

    # Create the virtual machine config spec
    config = vim.vm.ConfigSpec()
    config.name = name
    config.numCoresPerSocket = num_cores_per_socket
    config.numCPUs = num_cpus
    config.memoryMB = memory_gb * 1024

    # Create the clone spec
    clone_spec = vim.vm.CloneSpec()
    clone_spec.powerOn = False
    clone_spec.template = False
    clone_spec.config = config
    clone_spec.location = vim.vm.RelocateSpec()
    clone_spec.location.pool = dest_pool
    clone_spec.location.host = dest_host
    clone_spec.location.datastore = datastore

    # Clone the VM to create the new virtual machine
    WaitForTask(virtual_machine.CloneVM_Task(folder=folder, name=name, spec=clone_spec))
