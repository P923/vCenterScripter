from typing import List

from prettytable import PrettyTable
from pyVmomi import vim

MBFACTOR = float(1 << 20)


class Logger:
    def __init__(self, file: str= None):
        if file is not None:
            self.file = open(file, "w")
        else:
            self.file = None

    def print(self, string: str):
        string = string.replace("\n", "\n<D>")
        if self.file is not None:
            self.file.write(string)
        print("\t<D>:"+string)


def print_(string:str, logger:Logger):
    if logger is not None:
        logger.print(string)


def print_vm_info(virtual_machine: vim.VirtualMachine, logger: Logger):
    """
    Print information for a particular virtual machine or recurse into a
    folder with depth protection
    :param virtual_machine: The Virtual Machine
    :param logger: Logger
    """
    summary = virtual_machine.summary
    t = PrettyTable(['Name', 'Value'])

    t.add_row(["Name", summary.config.name])
    t.add_row(["Path", summary.config.vmPathName])
    t.add_row(["Guest", summary.config.guestFullName])
    t.add_row(["Instance UUID", summary.config.instanceUuid])
    t.add_row(["Bios UUID", summary.config.uuid])
    t.add_row(["Name", summary.config.name])
    t.add_row(["CPU", summary.config.numCpu])
    t.add_row(["RAM (MB)", summary.config.memorySizeMB])
    t.add_row(["VDisk", summary.config.numVirtualDisks])
    t.add_row(["ETH  Cards", summary.config.numEthernetCards])

    annotation = summary.config.annotation
    if annotation:
        t.add_row(["Annotation", annotation])

    t.add_row(["State", summary.runtime.powerState])
    if summary.guest is not None:
        ip_address = summary.guest.ipAddress
        tools_version = summary.guest.toolsStatus
        if tools_version is not None:
            t.add_row(["VMware-tools", tools_version])
        else:
            t.add_row(["VMware-tools", tools_version])
        if ip_address:
            t.add_row(["IP", ip_address])
        else:
            t.add_row(["IP", "None"])
    if summary.runtime.question is not None:
        t.add_row(["Question", summary.runtime.question.text])

    logger.print(t)


def print_pid_info(proc: vim.vm.guest.ProcessManager.ProcessInfo, logger: Logger):
    """
    Print the data from function get_info_pid
    :param proc: The process
    :param logger: Logger
    """
    temp = list()
    temp.append(proc)
    print_processes_list(temp, logger)


def print_processes_list(processes: List[vim.vm.guest.ProcessManager.ProcessInfo], logger: Logger):
    """
    Print the data taken from function get_processes
    :param processes:  List of processes taken using function get_processes
    :param logger: Logger
    """
    t = PrettyTable(['Name', 'PID', 'Owner', 'cmdLine', 'StartTime', 'EndTime', 'ExitCode'])

    for proc in processes:
        t.add_row([proc.name, proc.pid, proc.owner, proc.cmdLine, proc.startTime, proc.endTime, proc.exitCode])

    logger.print(t)


def print_host_info(host: vim.HostSystem, logger: Logger):
    """
    Print information for a particular Host
    :param host: The Host
    :param logger: Logger
    """
    summary = host.summary
    t = PrettyTable(['Name', 'Value'])

    t.add_row(["Name", host.name])
    t.add_row(["Boot Time", summary.runtime.bootTime])
    t.add_row(["PowerState", summary.runtime.powerState])
    t.add_row(["Maintenance", summary.runtime.inMaintenanceMode])
    t.add_row(["Status", host.overallStatus])
    t.add_row(["Parent", host.parent.name])
    t.add_row(["NICS", summary.hardware.numNics])
    t.add_row(["Management IP", summary.managementServerIp])
    t.add_row(["Fault Tolerance", summary.config.faultToleranceEnabled])
    t.add_row(["VMotion", summary.config.vmotionEnabled])
    t.add_row(["CPU Model", summary.hardware.cpuModel])
    t.add_row(["CPU Cores", summary.hardware.numCpuCores])
    t.add_row(["CPU Threads", summary.hardware.numCpuThreads])
    t.add_row(["CPU Threads", summary.hardware.numNics])

    host_cpu = summary.quickStats.overallCpuUsage
    host_total_cpu = round(summary.hardware.cpuMhz * summary.hardware.numCpuCores, 2)
    cpu_usage = round((host_cpu / host_total_cpu) * 100, 2)
    t.add_row(["CPU Total", host_total_cpu])
    t.add_row(["CPU % Used", cpu_usage])

    host_memory = summary.quickStats.overallMemoryUsage
    host_total_memory = round(summary.hardware.memorySize / 1024 / 1024,2)
    memory_usage = round((host_memory / host_total_memory) * 100, 2)
    t.add_row(["RAM (MB)", host_total_memory])
    t.add_row(["RAM usage (%)", memory_usage])

    logger.print(t)