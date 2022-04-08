"""Diskinfo LogicalDisk class definition

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

class LogicalDisk:
    """Class for logical disks/mount points"""    

    def __init__(self, system: object) -> None:
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

    def get_system(self) -> object:
        """Get the system this logical disk is present on."""
        return self._system

    def get_partitions(self) -> list:
        """Get all partitions that are part of this logical disk."""
        return self._partitions

    def add_partition(self, partition: object) -> None:
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
    def __init__(self, system: object) -> None:
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

    def __init__(self, logical_disk: object, system: object) -> None:
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
    
    def _set_description(self, logical_disk: object) -> None:
        """Set the description"""
        try:
            self._description = logical_disk.Description
            if not type(self._description) == str:
                self._description = ""
        except AttributeError:
            self._description = ""

    def _set_device_id_and_path_and_name(self, logical_disk: object) -> None:
        """Set the unique device ID and name. On windows this is pretty much the same as path."""
        try:
            self._device_id = logical_disk.DeviceID
            if not type(self._device_id) == str:
                self._device_id = ""
        except AttributeError:
            self._device_id = ""
        self._name = self._device_id
        self._path = self._device_id + "\\"

    def _set_drive_type(self, logical_disk: object) -> None:
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

    def _set_file_system(self, logical_disk: object) -> None:
        """Set the filesystem according to the system."""
        try:
            self._file_system = logical_disk.FileSystem
            if type(self._file_system) != str:
                self._file_system = "unknown"
        except AttributeError:
            self._file_system = "unknown"

    def _set_free_space(self, logical_disk: object) -> None:
        """Set the available space on the filesystem in bytes"""
        try:
            self._free_space = int(logical_disk.FreeSpace)
        except AttributeError:
            self._free_space = 0
        except ValueError:
            self._free_space = 0
        except TypeError:
            self._free_space = 0

    def _set_maximum_component_length(self, logical_disk: object) -> None:
        """Set the max path length in characters."""
        try:
            self._maximum_component_length = int(logical_disk.MaximumComponentLength)
        except AttributeError:
            self._maximum_component_length = 0
        except ValueError:
            self._maximum_component_length = 0
        except TypeError:
            self._maximum_component_length = 0

    def _set_size(self, logical_disk: object) -> None:
        """Set the size in bytes."""
        try:
            self._size = int(logical_disk.Size)
        except AttributeError:
            self._size = 0
        except ValueError:
            self._size = 0
        except TypeError:
            self._size = 0

    def _set_volume_name(self, logical_disk: object) -> None:
        """Set the volume name. Usually the Label value."""
        try:
            self._volume_name = logical_disk.VolumeName
            if type(self._volume_name) != str:
                self._volume_name = ""
        except AttributeError:
            self._volume_name = ""

    def _set_volume_serial_number(self, logical_disk: object) -> None:
        """Set the volume serial number."""
        try:
            self._volume_serial_number = logical_disk.VolumeSerialNumber
            if type(self._volume_serial_number) != str:
                self._volume_serial_number = ""
        except AttributeError:
            self._volume_serial_number = ""


