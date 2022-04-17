"""Diskinfo System class definition

Copyright (c) 2022 Lars Henrik Ericson

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from asyncio import subprocess
import sys
import os
import re
import socket
try:
    import platform
except ModuleNotFoundError:
    platform = None

from human_readable_units import UNITS, human_readable_units
from pydiskinfo_partition import DummyPartition

if sys.platform == 'win32':
    import wmi
    from pydiskinfo_logical_disk import WindowsLogicalDisk
    from pydiskinfo_partition import WindowsPartition
    from pydiskinfo_physical_disk import WindowsPhysicalDisk
elif sys.platform == 'linux':
    import subprocess
    try:
        import distro
    except ModuleNotFoundError:
        distro = None
    from pydiskinfo_logical_disk import LinuxLogicalDisk
    from pydiskinfo_partition import LinuxPartition
    from pydiskinfo_physical_disk import LinuxPhysicalDisk

class PyDiskInfoParseError(Exception):
    """General exception raised during system parsing. 
    
    It will be raised when parsing fails for some reason. The instance will 
    then be empty. Catching this exception will be the proper way to detect 
    that the instance should be diskarded. Usually any user have access to 
    this information. But if this is raised, it is usually because of access 
    rights."""

    def __init__(self, message, error):
        super().__init__(message, error)
        

class System(dict):
    """'abstractish' class describing a system.
    
    When you create a System object, a subclass is chosen depending on the 
    operating system of the host. So no pure System object will ever be created
    unless the object is unable to recognize the operating system. In that case 
    the object will be empty, excpet for some information about the operating 
    system itself. """

    def __new__(cls, name: str = None):
        """If on windows, create a WindowsSystem object instead."""
        created_object = None
        if sys.platform == "win32":
            created_object =  super().__new__(WindowsSystem)
        elif sys.platform == "linux":
            created_object =  super().__new__(LinuxSystem)
        else:
            created_object = System
        return created_object

    def __init__(self, name: str = None) -> None:
        self._set_name(name)
        self._set_type()
        self['Version'] = 'unknown'
        self['Physical Disks'] = []
        self['Partitions'] = []
        self['Logical Disks'] = []
        self._parse_system()

    def _set_type(self) -> None:
        if platform:
            self['Type'] = platform.system()
        else:
            self['Type'] = sys.platform

    def _set_name(self, name) -> None:
        if name:
            self['Name'] = name
        else:
            self['Name'] = socket.gethostname()
        
    def _parse_system(self) -> None:
        """If the system is of unknown type, nothing is parsed."""
        pass

    def __str__(self) -> str:
        system = 'System: ' + ", ".join((f'Name: {self["Name"]}', 
                                        f'Type/OS: {self["Type"]}',
                                        f'Version: {self["Version"]}'
                                        ))
        disks = ["\n".join(
                    ["  {}".format(line) for line in str(disk).split("\n")]
                ) for disk in self['Physical Disks']]
        return "\n".join((system, "", *disks))


class LinuxSystem(System):
    """This is the linux version of the System class.
    
    This class will take care of the special cases for when the module is 
    running on linux systems. The availability of certain files and tools 
    differ between linux distros and versions. Some info may be available
    as a regular user under some circumstances. But to get the module to 
    find all variables, you will probably have to run in with raised 
    privileges.
    
    """
        
    def __init__(self, name: str = None) -> None:
        super().__init__(name)
        self._set_version()
        

    def _set_version(self):
        """The distribution version of the system. 
        
        There is no 'one' way to get version information about a linux distro. 
        Kernel version would be easier, but is not really of any interest in the 
        scope of the pydiskinfo module. So we do as best we can, and default to 
        kernel version if all else fails."""
        if distro:
            self['Version'] = f'{distro.name()} {distro.version()}'
        elif platform:
            try:
                self['Version'] = platform.linux_distribution()
            except AttributeError:
                try:
                    self['Version'] = platform.dist()
                except AttributeError:
                    self['Version'] = f'{os.uname()[0]} {os.uname()[2]}'
        else:
            self['Version'] = f'{os.uname()[0]} {os.uname()[2]}'

    def _parse_system(self) -> None:
        block_devices = []
        try:
            with open('/proc/partitions', 'r') as proc_partitions:
                for each_line in proc_partitions:
                    match = re.match(r'\s*(\d+)\s+(\d+)\s+(\d+)\s+(\w+)\s*', each_line)
                    if match:
                        block_devices.append(match.group(1, 2, 3, 4))
        except FileNotFoundError as err:
            raise PyDiskInfoParseError('Missing /proc/partitions. Giving up parsing.') from err
        for each_device in block_devices:
            # handeling scsi hard drives
            if each_device[0] in ('8'):
                if not int(each_device[1]) // 16:
                    self['Physical Disks'].append(
                        LinuxPhysicalDisk(
                            self, 
                            int(each_device[0]),
                            int(each_device[1]),
                            int(each_device[2]),
                            each_device[3]
                        )
                    )
            # handeling metadisk (raid) devices
            elif each_device[0] == '9':
                # read from /proc/mdstat
                self['Physical Disks'].append(
                        LinuxPhysicalDisk(
                            self, 
                            int(each_device[0]),
                            int(each_device[1]),
                            int(each_device[2]),
                            each_device[3]
                        )
                    )
        for each_device in block_devices:
            if int(each_device[1]) > 0:
                disk = None
                for each_disk in self['Physical Disks']:
                    if str(each_disk['Major Number']) == each_device[0]:
                        disk = each_disk
                        break
                partition = LinuxPartition(disk, 
                                           int(each_device[0]), 
                                           int(each_device[1]),
                                           int(each_device[2]),
                                           each_device[3]
                                           )
                disk.add_partition(partition)
                self['Partitions'].append(partition)
        logical_disks = []
        try:
            mounts = subprocess.run((
                                        'df', 
                                        '--output=source,fstype,size,avail,target', 
                                        '--local',
                                        '--block-size=1'
                                    ),
                                    capture_output=True, 
                                    text=True
                                )
            for each_line in mounts.stdout.split('\n'):
                match = re.search(r'(.*\w)\s+(\w+)\s+(\d+)\s+(\d+)\s+(\/.*)', each_line)
                if match:
                    logical_disks.append(match.groups())
        except OSError as err:
            raise PyDiskInfoParseError('Cant find the "df" command.') from err
        for each_logical_disk in logical_disks:
            logical_disk = LinuxLogicalDisk(self, 
                                            each_logical_disk[4], 
                                            each_logical_disk[1], 
                                            int(each_logical_disk[2]),
                                            int(each_logical_disk[3])
                                            )
            for each_partition in self['Partitions']:
                if each_partition['Path'] == each_logical_disk[0]:
                    checked_logical_disk = self._add_logical_disk(logical_disk)
                    each_partition.add_logical_disk(checked_logical_disk)
                    checked_logical_disk.add_partition(each_partition)
            for each_disk in self['Physical Disks']:
                if each_disk['Path'] == each_logical_disk[0]:
                    checked_logical_disk = self._add_logical_disk(logical_disk)
                    dummy_partition = DummyPartition(each_disk, checked_logical_disk)
                    self['Partitions'].append(dummy_partition)
                    each_disk.add_partition(dummy_partition)
                    checked_logical_disk.add_partition(dummy_partition)
        
    def _add_logical_disk(self, logical_disk: 'LogicalDisk') -> 'LogicalDisk':
        return_logical_disk = None
        for each_logical_disk in self['Logical Disks']:
            if each_logical_disk['Name'] == logical_disk['Name']:
                return_logical_disk = each_logical_disk
                break
        if not return_logical_disk:
            return_logical_disk = logical_disk
            self['Logical Disks'].append(logical_disk)
        return return_logical_disk


class WindowsSystem(System):
    """This is the win32 version of the System class.
    
    This class will take care of the special cases when the module is runnning 
    on windows."""

    def __init__(self, name: str = None) -> None:
        super().__init__(name)
        self._set_version()

    def _set_version(self):
        self['Version'] = f'{platform.win32_edition()} {platform.win32_ver()[1]}'

    def _parse_system(self) -> None:
        """Parse the system"""
        try:
            cursor = wmi.WMI()            
        except wmi.x_access_denied as err:
            raise PyDiskInfoParseError('Access to wmi is denied.') from err
        except wmi.x_wmi_authentication as err:
            raise PyDiskInfoParseError('Authentication error when opening wmi') from err
        for each_disk in cursor.Win32_DiskDrive():
            disk = WindowsPhysicalDisk(each_disk, self)
            self['Physical Disks'].append(disk)
            for each_partition in each_disk.associators('Win32_DiskDriveToDiskPartition'):
                partition = WindowsPartition(each_partition, disk)
                new_partition = True
                for each_existing_partition in self['Partitions']:
                    if each_existing_partition['Device I.D.'] == partition['Device I.D.']:
                        partition = each_existing_partition
                        new_partition = False
                        break
                disk.add_partition(partition)
                if new_partition:
                    self['Partitions'].append(partition)
                for each_logical_disk in each_partition.associators('Win32_LogicalDiskToPartition'):
                    logical_disk = WindowsLogicalDisk(each_logical_disk, self)
                    new_logical_disk = True
                    for each_existing_logical_disk in self['Logical Disks']:
                        if each_existing_logical_disk['Device I.D.'] == logical_disk['Device I.D.']:
                            logical_disk = each_existing_logical_disk
                            new_logical_disk = False
                            break
                    if new_logical_disk:
                        self['Logical Disks'].append(logical_disk)
                    logical_disk.add_partition(partition)
                    partition.add_logical_disk(logical_disk)                  
        

