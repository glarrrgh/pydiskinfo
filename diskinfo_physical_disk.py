"""Diskinfo PhysicalDisk class definition

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


class PhysicalDisk:
    """Contains information about physical drives."""

    def __init__(self, system: object) -> None:
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

    def get_system(self) -> object:
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
    def __init__(self, system: object) -> None:
        super().__init__(system)


class WindowsPhysicalDisk(PhysicalDisk):
    """Subclass of PhysicalDrive that handles special windows situations"""
    def __init__(self, wmi_physical_disk: object, system: object) -> None:
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

    def _set_size(self, wmi_physical_disk: object) -> None:
        """set size of disk in bytes."""
        try:
            self._size = int(wmi_physical_disk.Size)
        except ValueError:
            self._size = -1

    def _set_disk_number(self, wmi_physical_disk: object) -> None:
        """set system disk identification number"""
        try:
            self._disk_number = int(wmi_physical_disk.Index)
        except ValueError:
            self._disk_number = -1

    def _set_device_id_and_path(self, wmi_physical_disk: object) -> None:
        try:
            self._path = wmi_physical_disk.DeviceID
            self._device_id = self._path
        except AttributeError:
            self._path = ""
            self._device_id = ""

    def _set_media_type(self, wmi_physical_disk: object) -> None:
        try:
            self._media_type = wmi_physical_disk.MediaType
        except AttributeError:
            self._media_type = ""

    def _set_serial_number(self, wmi_physical_disk: object) -> None:
        try:
            self._serial_number = wmi_physical_disk.SerialNumber
        except AttributeError:
            self._serial_number = ""

    def _set_model(self, wmi_physical_disk: object) -> None:
        try:
            self._model = wmi_physical_disk.Model
        except AttributeError:
            self._model = ""

    def _set_sectors(self, wmi_physical_disk: object) -> None:
        """Set total number of sectors, or -1 if not a number."""
        try:
            self._sectors = int(wmi_physical_disk.TotalSectors)
        except ValueError:
            self._sectors = -1

    def _set_heads(self, wmi_physical_disk: object) -> None:
        """Set total number of heads, or -1 if not a number"""
        try:
            self._heads = int(wmi_physical_disk.TotalHeads)
        except ValueError:
            self._heads = -1

    def _set_cylinders(self, wmi_physical_disk: object) -> None:
        """Set total number of cylinders, or -1 if not a number"""
        try:
            self._cylinders = int(wmi_physical_disk.TotalCylinders)
        except ValueError:
            self._cylinders = -1

    def _set_bytes_per_sector(self, wmi_physical_disk: object) -> None:
        """Set bytes per sector, or -1 if not a number"""
        try:
            self._bytes_per_sector = int(wmi_physical_disk.BytesPerSector)
        except ValueError:
            self._bytes_per_sector = -1

    def _set_firmware(self, wmi_physical_disk: object) -> None:
        """Set firmware"""
        try:
            self._firmware = wmi_physical_disk.FirmWare
        except AttributeError:
            self._firmware = "Unspecified"

    def _set_interface_type(self, wmi_physical_disk: object) -> None:
        try:
            self._interface_type = wmi_physical_disk.InterfaceType
        except AttributeError:
            self._interface_type = ""

    def _set_media_loaded(self, wmi_physical_disk: object) -> None:
        try:
            self._media_loaded = wmi_physical_disk.MediaLoaded
        except AttributeError:
            self._media_loaded = False

    def _set_status(self, wmi_physical_disk: object) -> None:
        try:
            self._status = wmi_physical_disk.Status
        except AttributeError:
            self._status = ""


