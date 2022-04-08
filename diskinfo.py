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
from human_readable_units import UNITS, human_readable_units

if sys.platform == 'win32':
    import wmi


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
        

class PhysicalDisk:
    """Contains information about physical drives."""

    def __init__(self, system: System) -> None:
        self._system = system
        self._partitions = []
        self._size = 0
        self._disk_number = -1
        self._device_id = ""
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
    
    def get_partitions(self) -> set:
        """Get a list of Partition objects connected to this disk."""
        return self._partitions

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
        return self._media_loaded
    
    def is_removable(self) -> bool:
        """Get wether disk is removable."""
        if self._media_type == "Removable Media":
            return True
        return False

    def __str__(self) -> str:
        """Overloading the string method"""
        disk = 'Disk -- ' + ", ".join(("Disk number: {}".format(self.get_disk_number()), 
                                       "Path: " + self.get_path(), 
                                       "Media Type: " + self.get_media_type(), 
                                       "Size: " + human_readable_units(self.get_size())
                                       ))
        partitions = ["\n".join(
                        ["  " + line for line in str(partition).split("\n")]) 
                      for partition in self._partitions]
        return "\n".join( (disk, *partitions, "" ) )

class LinuxPhysicalDisk(PhysicalDisk):
    def __init__(self, system: System) -> None:
        super().__init__(system)


class WindowsPhysicalDisk(PhysicalDisk):
    """Subclass of PhysicalDrive that handles special windows situations"""
    def __init__(self, wmi_physical_disk: wmi._wmi_object, system: System) -> None:
        super().__init__(system)
        self._set_size(wmi_physical_disk)
        self._set_disk_number(wmi_physical_disk)
        self._set_device_id_and_path(wmi_physical_disk)
        self._set_media_type(wmi_physical_disk)
        self._set_serial_number(wmi_physical_disk)
        self._set_model(wmi_physical_disk)
        self._set_sectors(wmi_physical_disk)
        self._set_heads(wmi_physical_disk)
        self._set_cylinders(wmi_physical_disk)
        self._set_bytes_per_sector(wmi_physical_disk)
        self._set_firmware(wmi_physical_disk)
        self._set_interface_type(wmi_physical_disk)
        self._set_media_loaded(wmi_physical_disk)
        self._set_status(wmi_physical_disk)
        
    def add_partition(self, partition: 'Partition') -> None:
        """add a Partition object to the disk."""
        self._partitions.append(partition)

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

    def _set_device_id_and_path(self, wmi_physical_disk: wmi._wmi_object) -> None:
        try:
            self._path = wmi_physical_disk.DeviceID
            self._device_id = self._path
        except AttributeError:
            self._path = ""
            self._device_id = ""

    def _set_media_type(self, wmi_physical_disk: wmi._wmi_object) -> None:
        try:
            self._media_type = wmi_physical_disk.MediaType
        except AttributeError:
            self._media_type = ""

    def _set_serial_number(self, wmi_physical_disk: wmi._wmi_object) -> None:
        try:
            self._serial_number = wmi_physical_disk.SerialNumber
        except AttributeError:
            self._serial_number = ""

    def _set_model(self, wmi_physical_disk: wmi._wmi_object) -> None:
        try:
            self._model = wmi_physical_disk.Model
        except AttributeError:
            self._model = ""

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

    def _set_interface_type(self, wmi_physical_disk: wmi._wmi_object) -> None:
        try:
            self._interface_type = wmi_physical_disk.InterfaceType
        except AttributeError:
            self._interface_type = ""

    def _set_media_loaded(self, wmi_physical_disk: wmi._wmi_object) -> None:
        try:
            self._media_loaded = wmi_physical_disk.MediaLoaded
        except AttributeError:
            self._media_loaded = False

    def _set_status(self, wmi_physical_disk: wmi._wmi_object) -> None:
        try:
            self._status = wmi_physical_disk.Status
        except AttributeError:
            self._status = ""


class Partition:
    """Contains information about partitions. This includes logical disk, 
    or 'volume' information. The same volume may span several disks, and the 
    filesystem of the partition, will in those cases be the filesystem of the 
    spanned volume. The partition may in that case not include a functional 
    filesystem on its own, though its contents will be part of one.
    """

    def __init__(self, disk: PhysicalDisk) -> None:
        self._disk = disk
        self._logical_disks = []
        self._blocksize = -1
        self._bootable = False
        self._boot_partition = False
        self._description = ""
        self._path = ""
        self._device_id = ""
        self._disk_number = -1
        self._partition_number = -1
        self._number_of_blocks = -1
        self._primary_partition = False
        self._size = 0
        self._starting_offset = -1
        self._type = ""

    def get_disk(self) -> PhysicalDisk:
        """Get the disk the partition is part of."""
        return self._disk

    def add_logical_disk(self, logical_disk: 'LogicalDisk') -> None:
        """Set the logical disk connected to this partition."""
        new_logical_disk = True
        for each_logical_disk in self._logical_disks:
            if each_logical_disk.get_device_id() == logical_disk.get_device_id():
                new_logical_disk = False
        if new_logical_disk:
            self._logical_disks.append(logical_disk)

    def get_logical_disks(self) -> set:
        """Get the logical disk connected to this partition."""
        return self._logical_disks

    def get_blocksize(self) -> int:
        """Get the blocksize of the partition."""
        return self._blocksize

    def is_bootable(self) -> bool:
        """If the partition is able to be used as a boot device."""
        return self._bootable

    def is_boot_partition(self) -> bool:
        """If the partition is a system boot partition."""
        return self._boot_partition

    def get_description(self) -> str:
        """A description of the system. Often includes partition table type."""
        return self._description

    def get_path(self) -> str:
        """Path to open partition for raw read. 
        
        Not available on windows. Open disk and use the starting offset and 
        size of the partition to raw read the partition.
        """
        return self._path

    def get_device_id(self) -> str:
        """Device id. It should be unique for the partition."""
        return self._device_id

    def get_disk_number(self) -> int:
        """Disk number of the parent disk of the partition."""
        return self._disk_number

    def get_partition_number(self) -> int:
        """The partition index on the disk. 
        
        Each disk may have a partition numbered 0.
        """
        return self._partition_number

    def Get_number_of_blocks(self) -> int:
        """The amount of blocks in the partition."""
        return self._number_of_blocks

    def is_primary_partition(self) -> bool:
        """If the partition is a primary partition."""
        return self._primary_partition

    def get_size(self) -> int:
        """Partition size in bytes."""
        return self._size

    def get_starting_offset(self) -> int:
        """Byte offset that the partition starts at."""
        return self._starting_offset

    def get_type(self) -> str:
        """A description of the partition type."""
        return self._type

    def __str__(self) -> str:
        """overloading the __str__ method"""
        partition = 'Partition -- ' + ", ".join(('ID: ' + self.get_device_id(), 
                                               'Type: ' + self.get_type(), 
                                               'Size: ' + human_readable_units(self.get_size()), 
                                               'Offset: '+ str(self.get_starting_offset())
                                               ))
        logical_disks = ["\n".join(["  " + line for line in str(logical_disk).split("\n")]) for logical_disk in self.get_logical_disks()] 
        return "\n".join((partition, *logical_disks))


class LinuxPartition(Partition):
    def __init__(self, disk: PhysicalDisk) -> None:
        super().__init__(disk)

class WindowsPartition(Partition):
    def __init__(self, partition: wmi._wmi_object, disk: PhysicalDisk) -> None:
        super().__init__(disk)
        self._set_blocksize(partition)
        self._set_bootable(partition)
        self._set_boot_partition(partition)
        self._set_description(partition)
        self._set_device_id(partition)
        self._set_disk_number(partition)
        self._set_partition_number(partition)
        self._set_number_of_blocks(partition)
        self._set_primary_partition(partition)
        self._set_size(partition)
        self._set_starting_offset(partition)
        self._set_type(partition)

    def _set_blocksize(self, partition: wmi._wmi_object) -> None:
        """Set blocksize or -1 if it fails."""
        try:
            self._blocksize = int(partition.BlockSize)
        except AttributeError:
            self._blocksize = -1
        except ValueError:
            self._blocksize = -1

    def _set_bootable(self, partition: wmi._wmi_object) -> None:
        """Set bootable or false if it fails."""
        try:
            self._bootable = partition.Bootable
        except AttributeError:
            self._bootable = False

    def _set_boot_partition(self, partition: wmi._wmi_object) -> None:
        """Set if system boot partition, or False if it fails."""
        try:
            self._boot_partition = partition.BootPartition
        except AttributeError:
            self._boot_partition = False

    def _set_description(self, partition: wmi._wmi_object) -> None:
        """set a description provided by the system."""
        try:
            self._description = partition.Description
        except AttributeError:
            self._description = ""

    def _set_device_id(self, partition: wmi._wmi_object) -> None:
        """set the device id provided by the system."""
        try:
            self._device_id = partition.DeviceID
        except AttributeError:
            self._device_id = ""

    def _set_disk_number(self, partition: wmi._wmi_object) -> None:
        """Set the disk index number as the system sees it."""
        try:
            self._disk_number = int(partition.DiskIndex)
        except AttributeError:
            self._disk_number = -1
        except ValueError:
            self._disk_number = -1

    def _set_partition_number(self, partition: wmi._wmi_object) -> None:
        """Set the partition index on the disk, according to the system."""
        try:
            self._partition_number = int(partition.Index)
        except AttributeError:
            self._partition_number = -1
        except ValueError:
            self._partition_number = -1

    def _set_number_of_blocks(self, partition: wmi._wmi_object) -> None:
        """Set number of blocks."""
        try:
            self._number_of_blocks = int(partition.NumberOfBlocks)
        except AttributeError:
            self._number_of_blocks = -1
        except ValueError:
            self._number_of_blocks = -1

    def _set_primary_partition(self, partition: wmi._wmi_object) -> None:
        """Set if the partition is a primary partition"""
        try:
            self._primary_partition = int(partition.PrimaryPartition)
        except AttributeError:
            self._primary_partition = False

    def _set_size(self, partition: wmi._wmi_object) -> None:
        """Set partition size in bytes."""
        try:
            self._size = int(partition.Size)
        except AttributeError:
            self._size = 0
        except ValueError:
            self._size = 0

    def _set_starting_offset(self, partition: wmi._wmi_object) -> None:
        """Set partition starting offset in bytes."""
        try:
            self._starting_offset = int(partition.StartingOffset)
        except AttributeError:
            self._starting_offset = -1
        except ValueError:
            self._starting_offset = -1

    def _set_type(self, partition: wmi._wmi_object) -> None:
        """Set partition type."""
        try:
            self._type = partition.Type
        except AttributeError:
            self._type = ""


class LogicalDisk:
    """Class for logical disks/mount points"""    

    def __init__(self, system: System) -> None:
        self._system = system
        self._partitions = set()
        self._description = ""
        self._device_id = ""
        self._drive_type = ""
        self._file_system = ""
        self._free_space = 0
        self._maximum_component_length = -1
        self._name = ""
        self._path = ""
        self._size = 0
        self._volume_name = ""
        self._volume_serial_number = ""

    def get_system(self) -> System:
        """Get the system this logical disk is present on."""
        return self._system

    def get_partitions(self) -> list:
        """Get all partitions that are part of this logical disk."""
        return self._partitions

    def add_partition(self, partition: Partition) -> None:
        """Add a partition to this logical disk"""
        self._partitions.add(partition)

    def get_description(self) -> str:
        """Get the system provided description of the logical disk"""
        return self._description

    def get_device_id(self) -> str:
        """Get the device ID"""
        return self._device_id

    def get_drive_type(self) -> str:
        """Get drive type."""
        return self._drive_type

    def get_file_system(self) -> str:
        """Get file system, according to the system"""
        return self._file_system

    def get_free_space(self) -> int:
        """Get free space on the filesystem."""
        return self._free_space

    def get_maximum_component_length(self) -> int:
        """Maximum path length, according to the system."""
        return self._maximum_component_length

    def get_name(self) -> str:
        """Often the same as path."""
        return self._name

    def get_path(self) -> str:
        """Get the mounted path to the logical disk. """
        return self._path

    def get_size(self) -> int:
        """Get the size of the logical disk."""
        return self._size

    def get_volume_name(self) -> str:
        """File system label value, or equivalent."""
        return self._volume_name

    def get_volume_serial_number(self) -> str:
        """File system serial number."""
        return self._volume_serial_number
    
    def __str__(self) -> str:
        return "Logical Disk -- " + ", ".join(("Path: " + self.get_path(), 
                                             'Label: ' + self.get_volume_name(),
                                             'File System: ' + self.get_file_system(),
                                             'Free Space: ' + human_readable_units(self.get_free_space())
                                           ))


class LinuxLogicalDisk(LogicalDisk):
    def __init__(self, system: System) -> None:
        super().__init__(system)

class WindowsLogicalDisk(LogicalDisk):
    _DRIVETYPES = [ 'Unknown', 
                    'No Root Directory', 
                    'Removable Disk', 
                    'Local Disk', 
                    'Network Drive', 
                    'Compact Disk',
                    'RAM Disk'
                    ]

    def __init__(self, logical_disk: wmi._wmi_object, system: System) -> None:
        super().__init__(system)
        self._set_description(logical_disk)
        self._set_device_id_and_path_and_name(logical_disk)
        self._set_drive_type(logical_disk)
        self._set_file_system(logical_disk)
        self._set_free_space(logical_disk)
        self._set_maximum_component_length(logical_disk)
        self._set_size(logical_disk)
        self._set_volume_name(logical_disk)
        self._set_volume_serial_number(logical_disk)
    
    def _set_description(self, logical_disk: wmi._wmi_object) -> None:
        """Set the description"""
        try:
            self._description = logical_disk.Description
            if not type(self._description) == str:
                self._description = ""
        except AttributeError:
            self._description = ""

    def _set_device_id_and_path_and_name(self, logical_disk: wmi._wmi_object) -> None:
        """Set the unique device ID and name. On windows this is pretty much the same as path."""
        try:
            self._device_id = logical_disk.DeviceID
            if not type(self._device_id) == str:
                self._device_id = ""
        except AttributeError:
            self._device_id = ""
        self._name = self._device_id
        self._path = self._device_id + "\\"

    def _set_drive_type(self, logical_disk: wmi._wmi_object) -> None:
        """Set the drive type."""
        try:
            drivetype = int(logical_disk.DriveType)
        except AttributeError:
            drivetype = 0
        except ValueError:
            drivetype = 0
        try:
            self._drive_type = self._DRIVETYPES[drivetype]
        except IndexError:
            self._drive_type = self._DRIVETYPES[0]

    def _set_file_system(self, logical_disk: wmi._wmi_object) -> None:
        """Set the filesystem according to the system."""
        try:
            self._file_system = logical_disk.FileSystem
            if type(self._file_system) != str:
                self._file_system = "unknown"
        except AttributeError:
            self._file_system = "unknown"

    def _set_free_space(self, logical_disk: wmi._wmi_object) -> None:
        """Set the available space on the filesystem in bytes"""
        try:
            self._free_space = int(logical_disk.FreeSpace)
        except AttributeError:
            self._free_space = 0
        except ValueError:
            self._free_space = 0
        except TypeError:
            self._free_space = 0

    def _set_maximum_component_length(self, logical_disk: wmi._wmi_object) -> None:
        """Set the max path length in characters."""
        try:
            self._maximum_component_length = int(logical_disk.MaximumComponentLength)
        except AttributeError:
            self._maximum_component_length = 0
        except ValueError:
            self._maximum_component_length = 0
        except TypeError:
            self._maximum_component_length = 0

    def _set_size(self, logical_disk: wmi._wmi_object) -> None:
        """Set the size in bytes."""
        try:
            self._size = int(logical_disk.Size)
        except AttributeError:
            self._size = 0
        except ValueError:
            self._size = 0
        except TypeError:
            self._size = 0

    def _set_volume_name(self, logical_disk: wmi._wmi_object) -> None:
        """Set the volume name. Usually the Label value."""
        try:
            self._volume_name = logical_disk.VolumeName
            if type(self._volume_name) != str:
                self._volume_name = ""
        except AttributeError:
            self._volume_name = ""

    def _set_volume_serial_number(self, logical_disk: wmi._wmi_object) -> None:
        """Set the volume serial number."""
        try:
            self._volume_serial_number = logical_disk.VolumeSerialNumber
            if type(self._volume_serial_number) != str:
                self._volume_serial_number = ""
        except AttributeError:
            self._volume_serial_number = ""


if __name__ == "__main__":
    system = System()
    print(str(system))
