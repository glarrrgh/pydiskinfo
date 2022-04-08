"""Diskinfo Partition class definition

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


class Partition:
    """Contains information about partitions. This includes logical disk, 
    or 'volume' information. The same volume may span several disks, and the 
    filesystem of the partition, will in those cases be the filesystem of the 
    spanned volume. The partition may in that case not include a functional 
    filesystem on its own, though its contents will be part of one.
    """

    def __init__(self, disk: object) -> None:
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

    def get_disk(self) -> object:
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
    def __init__(self, disk: object) -> None:
        super().__init__(disk)

class WindowsPartition(Partition):
    def __init__(self, partition: object, disk: object) -> None:
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

    def _set_blocksize(self, partition: object) -> None:
        """Set blocksize or -1 if it fails."""
        try:
            self._blocksize = int(partition.BlockSize)
        except AttributeError:
            self._blocksize = -1
        except ValueError:
            self._blocksize = -1

    def _set_bootable(self, partition: object) -> None:
        """Set bootable or false if it fails."""
        try:
            self._bootable = partition.Bootable
        except AttributeError:
            self._bootable = False

    def _set_boot_partition(self, partition: object) -> None:
        """Set if system boot partition, or False if it fails."""
        try:
            self._boot_partition = partition.BootPartition
        except AttributeError:
            self._boot_partition = False

    def _set_description(self, partition: object) -> None:
        """set a description provided by the system."""
        try:
            self._description = partition.Description
        except AttributeError:
            self._description = ""

    def _set_device_id(self, partition: object) -> None:
        """set the device id provided by the system."""
        try:
            self._device_id = partition.DeviceID
        except AttributeError:
            self._device_id = ""

    def _set_disk_number(self, partition: object) -> None:
        """Set the disk index number as the system sees it."""
        try:
            self._disk_number = int(partition.DiskIndex)
        except AttributeError:
            self._disk_number = -1
        except ValueError:
            self._disk_number = -1

    def _set_partition_number(self, partition: object) -> None:
        """Set the partition index on the disk, according to the system."""
        try:
            self._partition_number = int(partition.Index)
        except AttributeError:
            self._partition_number = -1
        except ValueError:
            self._partition_number = -1

    def _set_number_of_blocks(self, partition: object) -> None:
        """Set number of blocks."""
        try:
            self._number_of_blocks = int(partition.NumberOfBlocks)
        except AttributeError:
            self._number_of_blocks = -1
        except ValueError:
            self._number_of_blocks = -1

    def _set_primary_partition(self, partition: object) -> None:
        """Set if the partition is a primary partition"""
        try:
            self._primary_partition = int(partition.PrimaryPartition)
        except AttributeError:
            self._primary_partition = False

    def _set_size(self, partition: object) -> None:
        """Set partition size in bytes."""
        try:
            self._size = int(partition.Size)
        except AttributeError:
            self._size = 0
        except ValueError:
            self._size = 0

    def _set_starting_offset(self, partition: object) -> None:
        """Set partition starting offset in bytes."""
        try:
            self._starting_offset = int(partition.StartingOffset)
        except AttributeError:
            self._starting_offset = -1
        except ValueError:
            self._starting_offset = -1

    def _set_type(self, partition: object) -> None:
        """Set partition type."""
        try:
            self._type = partition.Type
        except AttributeError:
            self._type = ""


