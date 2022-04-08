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

from human_readable_units import human_readable_units
import sys


from human_readable_units import UNITS, human_readable_units
from diskinfo_logical_disk import LogicalDisk
from diskinfo_partition import Partition
from diskinfo_physical_disk import PhysicalDisk

if sys.platform == 'win32':
    import wmi
    from diskinfo_logical_disk import WindowsLogicalDisk
    from diskinfo_partition import WindowsPartition
    from diskinfo_physical_disk import WindowsPhysicalDisk


class DiskInfoParseError(Exception):
    """General exception raised during system parsing. 
    
    It will be raised when parsing fails for some reason. The instance will 
    then be empty. Catching this exception will be the proper way to detect 
    that the instance should be diskarded. Usually any user have access to 
    this information. But if this is raised, it is usually because of access 
    rights."""

    def __init__(self, message, status):
        super().__init__(message, status)
        self.message = "Failed to parse the system information"
        self.status = status


class System:
    """Reads and contains information about the block devices on the system.
    
    This is probably the only class you need to instanciate. It will contain 
    information about all diskovered block devices on the system. You can 
    access information based on physical drives, partitions on those drives, 
    and volumes(windows) or mount points(linux). """

    def __new__(cls, name: str = "System"):
        """If on windows, create a WIndowsSystem object instead."""
        created_object = None
        if sys.platform == "win32":
            created_object =  super().__new__(WindowsSystem)
        elif sys.platform == "linux":
            created_object =  super().__new__(LinuxSystem)
        else:
            created_object = System
        return created_object

    def __init__(self, name: str = "System") -> None:
        self._name = name
        self._type = "generic"
        self._disks = []
        self._partitions = []
        self._logical_disks = []
        self._parse_system()

    def get_name(self) -> str:
        """Return system name, as specified on instanciation"""
        return self._name

    def get_type(self) -> str:
        """Return system/OS type. This value depends on the subclass used."""
        return self._type

    def _parse_system(self) -> None:
        """To be overloaded by subclasses"""
        pass

    def __str__(self) -> str:
        system = ", ".join(("System name: {}".format(self.get_name()), 
                            "System type/OS: {}".format(self.get_type())
                            ))
        disks = ["\n".join(
                    ["  {}".format(line) for line in str(disk).split("\n")]
                ) for disk in self._disks]
        return "\n".join((system, "", *disks))


class LinuxSystem(System):
    def _parse_system(self) -> None:
        pass


class WindowsSystem(System):
    """This is an inherited version of the System class.
    
    This class will take care of the special cases when the module is runnning 
    on windows."""

    def __init__(self, name: str = "Windows System") -> None:
        super().__init__(name)
        self._type = "Microsoft Windows"  

    def _parse_system(self) -> None:
        """Parse the system"""
        try:
            cursor = wmi.WMI()            
        except wmi.x_access_denied as err:
            raise DiskInfoParseError from err
        except wmi.x_wmi_authentication as err:
            raise DiskInfoParseError from err
        for each_disk in cursor.Win32_DiskDrive():
            disk = WindowsPhysicalDisk(each_disk, self)
            self._disks.append(disk)
            for each_partition in each_disk.associators('Win32_DiskDriveToDiskPartition'):
                partition = WindowsPartition(each_partition, disk)
                new_partition = True
                for each_existing_partition in self._partitions:
                    if each_existing_partition.get_device_id() == partition.get_device_id():
                        partition = each_existing_partition
                        new_partition = False
                        break
                disk.add_partition(partition)
                if new_partition:
                    self._partitions.append(partition)
                for each_logical_disk in each_partition.associators('Win32_LogicalDiskToPartition'):
                    logical_disk = WindowsLogicalDisk(each_logical_disk, self)
                    new_logical_disk = True
                    for each_existing_logical_disk in self._logical_disks:
                        if each_existing_logical_disk.get_device_id() == logical_disk.get_device_id():
                            logical_disk = each_existing_logical_disk
                            new_logical_disk = False
                            break
                    if new_logical_disk:
                        self._logical_disks.append(logical_disk)
                    logical_disk.add_partition(partition)
                    partition.add_logical_disk(logical_disk)                  
        

