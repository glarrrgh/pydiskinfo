"""A module for getting information about block devices in a system.

The diskinfo module is not a replacement for modules for gaining 
file or filesystem information. It is mostly a supplement, for those 
rare situations when you need to know more about the physical devices rather 
than the filesystems and files on them. I made the module because I needed 
path information to be able to read byte for byte off of hard drives. If other 
uses arise, I may be compelled to extend the module.

The module depends on the wmi module, when run on a windows system. No
extra modules need to be installed on linux systems. The linux functionality 
depends heavily on sysfs, so it will probably not work on other unix like systems, 
that often do not come with sysfs.

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

import sys

if sys.platform == 'win32':
    import wmi

MEDIA_TYPES = []


class DiskInfoParseError(Exception):
    """General exception raised during system parsing. 
    
    It will be raised when parsing fails for some reason. The instance will 
    then be empty. Catching this exception will be the proper way to detect 
    that the instance should be discarded. Usually any user have access to 
    this information. But if this is raised, it is usually because of access 
    rights."""

    def __init__(self, message, status):
        super().__init__(message, status)
        self.message = "Failed to parse the system information"
        self.status = status


class System:
    """Reads and contains information about the block devices on the system.
    
    This is probably the only class you need to instanciate. It will contain 
    information about all discovered block devices on the system. You can 
    access information based on physical drives, partitions on those drives, 
    and volumes(windows) or mount points(linux). """

    def __new__(cls, name: str = "System"):
        """If on windows, create a WIndowsSystem object instead."""
        created_object = None
        if sys.platform == "win32":
            created_object =  super().__new__(WindowsSystem)
        elif sys.platform == "linux":
            created_object =  super().__new__(LinuxSystem)
        return created_object

    def __init__(self, name: str = "System") -> None:
        self._name = name
        self._drives = []
        self._partitions = []
        self._volumes = []
        self._parse_system()

    def _parse_system(self) -> None:
        """To be overloaded by subclasses"""
        pass

    def __str__(self) -> str:
        return repr(self._drives)

class LinuxSystem(System):
    def _parse_system(self) -> None:
        pass

class WindowsSystem(System):
    """This is an inherited version of the System class.
    
    This class will take care of the special cases when the module is runnning 
    on windows."""  

    def _parse_system(self) -> None:
        """Parse the system"""
        try:
            cursor = wmi.WMI()            
        except wmi.x_access_denied as err:
            raise DiskInfoParseError from err
        except wmi.x_wmi_authentication as err:
            raise DiskInfoParseError from err
        self._drives = [WindowsPhysicalDrive(drive) for drive in cursor.Win32_DiskDrive()]
        self._volumes = [WindowsVolume(volume) for volume in cursor.Win32_DiskDrive())]
        self._partitions = [WindowsPartition(partition) for partition in cursor.Win32_DiskPartition()]


class PhysicalDrive:
    """Contains information about physical drives."""

    def __init__(self) -> None:
        self._partitions = []
        self._size = 0
        self._drive_number = 0
        self._path = ""
        self._media_type = ""
        self._serial_number = ""
        self._model = ""
        self._sectors = 0
        self._heads = 0
        self._cylinders = 0
        self._bytes_per_sector = 0
        self._firmware = ""
        self._disk_number = -1
        self._interface_type = ""
        self._media_loaded = False
        self._status = ""
    
    def get_path(self) -> str:
        """Get a path usable for raw access."""
        return self.path

    def get_size(self) -> int:
        """Get the disk size in bytes."""
        return str(self.size)

    def is_removable(self) -> bool:
        """Get wether disk is removable"""
        if self.media_type == "Removable Media":
            return True
        return False

    def get_type(self) -> str:
        """Get the disk type"""
        return self.media_type

    def get_partitions(self) -> list:
        """Get a list of partition objects"""
        return self.partitions[:]

    def get_caption(self) -> str:
        """Get model name and maybe manufacturer"""
        return self.caption
    
    def set_path(self, path: str) -> None:
        """Set drive access path and drive number."""
        self.path = path

    def __str__(self) -> str:
        """Overloading the string method"""
        disk = ", ".join((self.get_caption(), self.get_path(), self.get_type(), self.get_size()))
        partitions = ["\n".join(["    " + line for line in str(partition).split("\n")]) for partition in self.partitions]
        try:   
            return "\n".join( (disk, *partitions ) )
        except IndexError:
            return disk


class WindowsPhysicalDrive(PhysicalDrive):
    """Subclass of PhysicalDrive that handles special windows situations"""
    def __init__(self, wmi_physical_disk: wmi._wmi_object) -> None:
        super().__init__()
        self._set_partitions(wmi_physical_disk)
        self._set_size(wmi_physical_disk)
        self._set_drive_number(wmi_physical_disk)
        self.path = wmi_physical_disk.DeviceID
        self._set_media_type = 
        
    def _set_partitions(self, wmi_physical_disk: wmi._wmi_object) -> None:
        """Private method that parses the partitons"""
        self.partitions = [ WindowsPartition(partition, self) for partition in wmi_physical_disk.associators('Win32_DiskDriveToDiskPartition') ]

    def _set_size(self, wmi_physical_disk: wmi._wmi_object) -> None:
        """set size of disk in bytes."""
        try:
            self.size = int(wmi_physical_disk.Size)
        except ValueError:
            self.size = -1

    def _set_drive_number(self, wmi_physical_disk: wmi._wmi_object) -> None:
        """set system drive identification number"""
        try:
            self.disk_number = int(wmi_physical_disk.Index)
        except IndexError:
            self.disk_number = -1
        except ValueError:
            self.path = ""
            self.disk_number = -1



class Partition():
    """Contains information about partitions. This includes logical disk, 
    or 'volume' information. The same volume may span several disks, and the 
    filesystem of the partition, will in those cases be the filesystem of the 
    spanned volume. The partition may in that case not include a functional 
    filesystem on its own, though its contents will be part of one.
    """

    def __init__(self, partition) -> None:
        self._partition = partition
        self.disk = None
        self.volume = None
        self._set_volumes()
        self._set_size()
        self._set_partition_table_type()
        self._set_descriptor()

    def get_size(self) -> int:
        """Get the partition size in bytes."""
        return self.size

    def get_descriptor(self) -> str:
        """Get a descriptor of the partition"""
        return self.descriptor

    def get_partiton_table_type(self) -> str:
        """get the partition table type"""
        return self.partition_table_type

    def _set_descriptor(self) -> None:
        """private: extract partition descriptor from a wmi object"""
        self.descriptor = self._partition.Name

    def _set_volumes(self) -> None:
        """Private: parse the logical disks"""
        self.volumes = [ Volume(volume) for volume in self._partition.associators('Win32_LogicalDiskToPartition')]

    def _set_size(self) -> None:
        """private: extract size from a wmi object"""
        try:
            self.size = int(self._partition.Size)
        except ValueError:
            self.size = 0

    def _set_partition_table_type(self) -> None:
        """private: extract partition table type from a wmi object"""
        self.partition_table_type = self._partition.Type

    def __str__(self) -> str:
        """overloading the __str__ method"""
        partition = ", ".join((self.get_descriptor(), self.get_partiton_table_type(), str(self.get_size())))
        volumes = []
        volumes = ["\n".join(["    " + line for line in str(volume).split("\n")]) for volume in self.volumes]
        try:
            return "\n".join((partition, *volumes))
        except IndexError:
            return partition


class Volume(object):
    def __init__(self, volume) -> None:
        self._volume = volume
        self._set_name()
        self._set_filesystem()

    def get_file_system(self) -> str:
        """Get filesystem type"""
        return self.file_system

    def get_name(self) -> str:
        """Get the volume path letter."""
        return self.name

    def _set_filesystem(self) -> None:
        """Private: Extracts the filesystem type from a wmi object"""
        if isinstance(self._volume.FileSystem, str):
            self.file_system = self._volume.FileSystem
        else:
            self.file_system = ""

    def _set_name(self) -> None:
        """Private: Extracts the volume name from a wmi object"""
        if isinstance(self._volume.Name, str):
            self.name = self._volume.Name
        else:
            self.name = ""
    
    def __str__(self) -> str:
        """overloading the __str__ method"""
        return ", ".join((self.get_name(), self.get_file_system()))


def get_disks(computer: str = "", username: str = "", password: str = "") -> list:
    """Reads the system information and returns a list of disk information.
    The list consist of Disk objects. The Disk object will include the partiton
    objects

    You may supply computer, username and password to connect to other
    computers. But no concideration is taken for the protection of credentials
    in memory. Username need to include domain/workgroup. Like domain\\username
    """
    try:
        wmi_cursor = wmi.WMI(computer=computer, user=username, password=password)
    except wmi.x_access_denied as err:
        return None
    except wmi.x_wmi_authentication as err:
        return None
    disks = [PhysicalDrive(physical_disk) for physical_disk in wmi_cursor.Win32_DiskDrive()]
    return disks


if __name__ == "__main__":
    disk = System()
    print(str(disk))
