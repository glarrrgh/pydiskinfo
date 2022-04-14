"""pydiskinfo PhysicalDisk class definition

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


class PhysicalDisk(dict):
    """Contains information about physical drives."""

    def __init__(self, system: 'System') -> None:
        self['System'] = system
        self['Partitions'] = []
        self['Size'] = 0
        self['Disk Number'] = -1
        self['Device I.D.'] = ""
        self['Path'] = ""
        self['Media Type'] = ""
        self['Serial Number'] = ""
        self['Model'] = ""
        self['Sectors'] = 0
        self['Heads'] = 0
        self['Cylinders'] = 0
        self['Bytes per Sector'] = 0
        self['Firmware Version'] = ""
        self['Interface Type'] = ""
        self['Media Loaded'] = False
        self['Status'] = ""

    def __str__(self) -> str:
        """Overloading the string method"""
        disk = 'Disk -- ' + ", ".join(("Disk Number: {}".format(self['Disk Number']), 
                                       "Path: " + self['Path'], 
                                       "Media Type: " + self['Media Type'], 
                                       "Size: " + human_readable_units(self['Size'])
                                       ))
        partitions = ["\n".join(
                        ["  " + line for line in str(partition).split("\n")]) 
                      for partition in self['Partitions']]
        return "\n".join( (disk, *partitions, "" ) )

class LinuxPhysicalDisk(PhysicalDisk):
    def __init__(self, 
                system: 'System', 
                major_number: int, 
                minor_number: int,
                size_in_sectors: int,
                device_name: str
                ) -> None:
        super().__init__(system)
        self['Major Number'] = major_number
        self['Minor Number'] = minor_number
        self._set_name_and_path(device_name)
        self._set_size_and_sectors(size_in_sectors)

    def _set_size_and_sectors(self, sectors: int, sector_size: int = 512) -> None:
        """Sets number of sectors, sectors size, and size in bytes."""
        self['Sectors'] = sectors
        self['Bytes per Sector'] = sector_size
        self['Size'] = sectors * sector_size

    def _add_partition(self, partition: 'Partition') -> None:
        """Adds a partition to the pysical disk."""
        self['Partitions'].append(partition)

    def _set_name_and_path(self, name):
        self['Name'] = name
        self['Path'] = f'/dev/{name}'
        


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
        self['Partitions'].append(partition)

    def _set_size(self, wmi_physical_disk: 'wmi._wmi_object') -> None:
        """set size of disk in bytes."""
        try:
            self['Size'] = int(wmi_physical_disk.Size)
        except ValueError:
            self['Size'] = -1

    def _set_disk_number(self, wmi_physical_disk: 'wmi._wmi_object') -> None:
        """set system disk identification number"""
        try:
            self['Disk Number'] = int(wmi_physical_disk.Index)
        except ValueError:
            self['Disk Number'] = -1

    def _set_device_id_and_path(self, wmi_physical_disk: 'wmi._wmi_object') -> None:
        try:
            self['Path'] = wmi_physical_disk.DeviceID
            self['Device I.D.'] = self['Path']
        except AttributeError:
            self['Path'] = ""
            self['Device I.D.'] = ""

    def _set_media_type(self, wmi_physical_disk: 'wmi._wmi_object') -> None:
        try:
            self['Media Type'] = wmi_physical_disk.MediaType
        except AttributeError:
            self['Media Type'] = ""

    def _set_serial_number(self, wmi_physical_disk: 'wmi._wmi_object') -> None:
        try:
            self['Serial Number'] = wmi_physical_disk.SerialNumber
        except AttributeError:
            self['Serial Number'] = ""

    def _set_model(self, wmi_physical_disk: 'wmi._wmi_object') -> None:
        try:
            self['Model'] = wmi_physical_disk.Model
        except AttributeError:
            self['Model'] = ""

    def _set_sectors(self, wmi_physical_disk: 'wmi._wmi_object') -> None:
        """Set total number of sectors, or -1 if not a number."""
        try:
            self['Sectors'] = int(wmi_physical_disk.TotalSectors)
        except ValueError:
            self['Sectors'] = -1

    def _set_heads(self, wmi_physical_disk: 'wmi._wmi_object') -> None:
        """Set total number of heads, or -1 if not a number"""
        try:
            self['Heads'] = int(wmi_physical_disk.TotalHeads)
        except ValueError:
            self['Heads'] = -1

    def _set_cylinders(self, wmi_physical_disk: 'wmi._wmi_object') -> None:
        """Set total number of cylinders, or -1 if not a number"""
        try:
            self['Cylinders'] = int(wmi_physical_disk.TotalCylinders)
        except ValueError:
            self['Cylinders'] = -1

    def _set_bytes_per_sector(self, wmi_physical_disk: 'wmi._wmi_object') -> None:
        """Set bytes per sector, or -1 if not a number"""
        try:
            self['Bytes per Sector'] = int(wmi_physical_disk.BytesPerSector)
        except ValueError:
            self['Bytes per Sector'] = -1

    def _set_firmware(self, wmi_physical_disk: 'wmi._wmi_object') -> None:
        """Set firmware"""
        try:
            self['Firmware'] = wmi_physical_disk.FirmWare
        except AttributeError:
            self['Firmware'] = "Unspecified"

    def _set_interface_type(self, wmi_physical_disk: 'wmi._wmi_object') -> None:
        try:
            self['Interface_type'] = wmi_physical_disk.InterfaceType
        except AttributeError:
            self['Interface_type'] = ""

    def _set_media_loaded(self, wmi_physical_disk: 'wmi._wmi_object') -> None:
        try:
            self['Media Loaded'] = wmi_physical_disk.MediaLoaded
        except AttributeError:
            self['Media Loaded'] = False

    def _set_status(self, wmi_physical_disk: 'wmi._wmi_object') -> None:
        try:
            self['Status'] = wmi_physical_disk.Status
        except AttributeError:
            self['Status'] = ""


