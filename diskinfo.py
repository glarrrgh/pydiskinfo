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

from logging.config import valid_ident
import sys

if sys.platform == 'win32':
    import wmi

UNITS = { '': 1,
          'K': 1_000, 
          'M': 1_000_000, 
          'G': 1_000_000_000, 
          'T': 1_000_000_000_000, 
          'P': 1_000_000_000_000_000,
          'B': 1,
          'KB': 1_000, 
          'MB': 1_000_000, 
          'GB': 1_000_000_000, 
          'TB': 1_000_000_000_000, 
          'PB': 1_000_000_000_000_000,
          'KiB': 1_024, 
          'MiB': pow(1_024, 2), 
          'GiB': pow(1_024, 3), 
          'TiB': pow(1_024, 4), 
          'PiB': pow(1_024, 5)
        }

def human_readable_units(value: int, unit: str = 'auto', type: str = 'B') -> str:
    """Converts an int to a string with a unit. 
    
       If unit is omitted, the function will choose a fitting unit.
       If unit is omitted, and type is omitted, it will choose something like 
       KB. type can be 
            'B': decimal bytes (KB for instance)
            'M': no bytes (K for instance)
            'I': binary bytes (KiB for instance)
       If unit is specified, type will be ignored.
    """
    if unit == 'auto':
        if type == 'M':
            for each_unit in ('P', 'T', 'G', 'M', 'K', ''):
                return_value = value/UNITS[each_unit]
                if return_value > 1:
                    return_unit = each_unit
                    break
        elif type == 'I':
            for each_unit in ('PiB', 'TiB', 'GiB', 'MiB', 'KiB', 'B'):
                return_value = value/UNITS[each_unit]
                if return_value > 1:
                    return_unit = each_unit
                    break
        else:
            for each_unit in ('PB', 'TB', 'GB', 'MB', 'KB', 'B'):
                return_value = value/UNITS[each_unit]
                if return_value > 1:
                    return_unit = each_unit
                    break        
    else:
        return_unit = unit
        try:
            return_value = value/UNITS[unit]
        except KeyError:
            raise ReadableUnitError
    return "{:.3f}{}".format(return_value, return_unit)


class ReadableUnitError(Exception):
    """Exception raised if unit specified is not in dict UNITS"""
    def __init__(self, message, status):
        super().__init__(message, status)
        self.message = "unit specified not found in UNITS"
        self.status = status


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
        self._type = "generic"
        self._disks = []
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
        system = ", ".join(("System name: {}".format(self.get_name()), "System type/OS: {}".format(self.get_type())))
        disks = ["\n".join(["  {}".format(line) for line in str(disk).split("\n")]) for disk in self._disks]
        return "\n".join((system, *disks))


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
        self._disks = [WindowsPhysicalDisk(disk, self) for disk in cursor.Win32_DiskDrive()]
        

class PhysicalDisk:
    """Contains information about physical drives."""

    def __init__(self, system: System) -> None:
        self._system = system
        self._partitions = []
        self._size = 0
        self._drive_number = -1
        self._path = ""
        self._media_type = ""
        self._serial_number = ""
        self._model = ""
        self._sectors = 0
        self._heads = 0
        self._cylinders = 0
        self._bytes_per_sector = 0
        self._firmware = ""
        self._interface_type = ""
        self._media_loaded = False
        self._status = ""

    def get_system(self) -> System:
        """Get the system that this disk is connected to."""
        return self._system
    
    def get_partitions(self) -> list:
        """Get a copy of the list of Partition objects connected to this disk."""
        return self._partitions[:]

    def get_size(self) -> int:
        """Get the disk size in bytes."""
        return self._size

    def get_path(self) -> str:
        """Get a path usable for raw access."""
        return self._path

    def get_media_type(self) -> str:
        """Get the media type of this disk."""
        return self._media_type

    def get_serial_number(self) -> str:
        """Get disk serial number."""
        return self._serial_number

    def get_model(self) -> str:
        """Get disk model. This often includes hints of the manufacturer."""
        return self._model

    def get_sectors(self) -> int:
        """Get the number of sectors on disk."""
        return self._sectors

    def get_heads(self) -> int:
        """Get the number of heads on disk."""
        return self._heads

    def get_cylinders(self) -> int:
        """Get the number of cylinders on disk."""
        return self._cylinders

    def get_bytes_per_sector(self) -> int:
        """Get bytes per sector. This often translates to blocksize."""
        return self._bytes_per_sector

    def get_firmware_version(self) -> str:
        """Get disk firmware version. """
        return self._firmware

    def get_disk_number(self) -> int:
        """Get disk number, as reported by the os."""
        return self._disk_number

    def get_interface_type(self) -> str:
        """Get interface type. 
        
        Value may be missleading, as some systems may reuse legacy interface 
        names for newer interface types. 
        """
        return self._interface_type

    def get_status(self) -> str:
        """Get the status of the disk. """
        return self._status

    def is_media_loaded(self) -> bool:
        """Is some media inserted in drive. 
        
        May make a difference on card readers and such.
        """
    
    def is_removable(self) -> bool:
        """Get wether disk is removable."""
        if self._media_type == "Removable Media":
            return True
        return False

    def __str__(self) -> str:
        """Overloading the string method"""
        disk = ", ".join(("Disk {}".format(self.get_disk_number()), self.get_path(), self.get_media_type(), human_readable_units(self.get_size())))
        partitions = ["\n".join(["  " + line for line in str(partition).split("\n")]) for partition in self._partitions]
        return "\n".join( (disk, *partitions ) )

class LinuxPhysicalDisk(PhysicalDisk):
    pass


class WindowsPhysicalDisk(PhysicalDisk):
    """Subclass of PhysicalDrive that handles special windows situations"""
    def __init__(self, wmi_physical_disk: wmi._wmi_object, system: System) -> None:
        super().__init__(system)
        self._set_partitions(wmi_physical_disk)
        self._set_size(wmi_physical_disk)
        self._set_disk_number(wmi_physical_disk)
        self._path = wmi_physical_disk.DeviceID
        self._set_media_type = wmi_physical_disk.MediaType
        self._serial_number = wmi_physical_disk.SerialNumber
        self._model = wmi_physical_disk.Model
        self._set_sectors(wmi_physical_disk)
        self._set_heads(wmi_physical_disk)
        self._set_cylinders(wmi_physical_disk)
        self._set_bytes_per_sector(wmi_physical_disk)
        self._set_firmware(wmi_physical_disk)
        self._interface_type = wmi_physical_disk.InterfaceType
        self._media_loaded = wmi_physical_disk.MediaLoaded
        self._status = wmi_physical_disk.Status
        
    def _set_partitions(self, wmi_physical_disk: wmi._wmi_object) -> None:
        """Private method that parses the partitons"""
        self._partitions = [ WindowsPartition(partition, self) for partition in wmi_physical_disk.associators('Win32_DiskDriveToDiskPartition') ]

    def _set_size(self, wmi_physical_disk: wmi._wmi_object) -> None:
        """set size of disk in bytes."""
        try:
            self._size = int(wmi_physical_disk.Size)
        except ValueError:
            self._size = -1

    def _set_disk_number(self, wmi_physical_disk: wmi._wmi_object) -> None:
        """set system disk identification number"""
        try:
            self._disk_number = int(wmi_physical_disk.Index)
        except ValueError:
            self._disk_number = -1

    def _set_sectors(self, wmi_physical_disk: wmi._wmi_object) -> None:
        """Set total number of sectors, or -1 if not a number."""
        try:
            self._sectors = int(wmi_physical_disk.TotalSectors)
        except ValueError:
            self._sectors = -1

    def _set_heads(self, wmi_physical_disk: wmi._wmi_object) -> None:
        """Set total number of heads, or -1 if not a number"""
        try:
            self._heads = int(wmi_physical_disk.TotalHeads)
        except ValueError:
            self._heads = -1

    def _set_cylinders(self, wmi_physical_disk: wmi._wmi_object) -> None:
        """Set total number of cylinders, or -1 if not a number"""
        try:
            self._cylinders = int(wmi_physical_disk.TotalCylinders)
        except ValueError:
            self._cylinders = -1

    def _set_bytes_per_sector(self, wmi_physical_disk: wmi._wmi_object) -> None:
        """Set bytes per sector, or -1 if not a number"""
        try:
            self._bytes_per_sector = int(wmi_physical_disk.BytesPerSector)
        except ValueError:
            self._bytes_per_sector = -1

    def _set_firmware(self, wmi_physical_disk: wmi._wmi_object) -> None:
        """Set firmware"""
        try:
            self._firmware = wmi_physical_disk.FirmWare
        except AttributeError:
            self._firmware = "Unspecified"


class Partition:
    """Contains information about partitions. This includes logical disk, 
    or 'volume' information. The same volume may span several disks, and the 
    filesystem of the partition, will in those cases be the filesystem of the 
    spanned volume. The partition may in that case not include a functional 
    filesystem on its own, though its contents will be part of one.
    """

    def __init__(self, disk: PhysicalDisk) -> None:
        self.disk = disk

    def get_size(self) -> int:
        """Get the partition size in bytes."""
        return self.size

    def get_descriptor(self) -> str:
        """Get a descriptor of the partition"""
        return self.descriptor

    def get_partiton_table_type(self) -> str:
        """get the partition table type"""
        return self.partition_table_type

    def __str__(self) -> str:
        """overloading the __str__ method"""
        partition = ", ".join((self.get_descriptor(), self.get_partiton_table_type(), human_readable_units(self.get_size())))
        return "\n".join((partition, ))


class LinuxPartition(Partition):
    pass

class WindowsPartition(Partition):
    def __init__(self, partition: wmi._wmi_object, disk: PhysicalDisk) -> None:
        super().__init__(disk)
        self._set_descriptor(partition)
        self._set_size(partition)
        self._set_partition_table_type(partition)

    def _set_descriptor(self, partition: wmi._wmi_object) -> None:
        """private: extract partition descriptor from a wmi object"""
        self.descriptor = partition.Name

    def _set_size(self, partition: wmi._wmi_object) -> None:
        """private: extract size from a wmi object"""
        try:
            self.size = int(partition.Size)
        except ValueError:
            self.size = 0

    def _set_partition_table_type(self, partition: wmi._wmi_object) -> None:
        """private: extract partition table type from a wmi object"""
        self.partition_table_type = partition.Type

    


class LogicalDisk:
    """Class for logical disks/mount points"""    
    
    def __str__(self) -> str:
        return "Logical Disk"


class LinuxLogicalDisk(LogicalDisk):
    pass

class WindowsLogicalDisk(LogicalDisk):
    pass


if __name__ == "__main__":
    system = System()
    print(str(system))
