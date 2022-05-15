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
from typing import List, Tuple
import sys
import socket
try:
    import platform
except ModuleNotFoundError:
    platform = None
from . system_component import SystemComponent
from . human_readable_units import human_readable_units


class System(SystemComponent):
    """'abstractish' class describing a system.

    When you create a System object, a subclass is chosen depending on the
    operating system of the host. So no pure System object will ever be created
    unless the object is unable to recognize the operating system. In that case
    the object will be empty, excpet for some information about the operating
    system itself. """

    def __init__(self, name: str = None) -> None:
        self._set_name(name)
        self._set_type()
        self['Version'] = 'unknown'
        self._physical_disks: list['PhysicalDisk'] = []
        self._partitions: list['Partition'] = []
        self._logical_disks: list['LogicalDisk'] = []
        self._parse_system()

    def get_physical_disks(self) -> tuple['PhysicalDisk']:
        return tuple(self._physical_disks)

    def get_partitions(self) -> tuple['Partition']:
        return tuple(self._partitions)

    def get_logical_disks(self) -> tuple['LogicalDisk']:
        return tuple(self._logical_disks)

    def _add_logical_disk(self, logical_disk: 'LogicalDisk') -> 'LogicalDisk':
        for each_existing_logical_disk in self.get_logical_disks():
            if (
                each_existing_logical_disk['Device I.D.'] ==
                logical_disk['Device I.D.']
            ):
                return each_existing_logical_disk
        self._logical_disks.append(logical_disk)
        return logical_disk

    def _add_partition(self, partition: 'Partition') -> 'Partition':
        for each_existing_partition in self.get_partitions():
            if (
                each_existing_partition['Device I.D.'] ==
                partition['Device I.D.']
            ):
                return each_existing_partition
        self._partitions.append(partition)
        return partition

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
        system = 'System: ' + ", ".join((
            f'Name: {self["Name"]}',
            f'Type/OS: {self["Type"]}',
            f'Version: {self["Version"]}'
        ))
        disks = ["\n".join(
                    ["  {}".format(line) for line in str(disk).split("\n")]
                ) for disk in self.get_physical_disks()]
        return "\n".join((system, "", *disks))


class LogicalDisk(SystemComponent):
    """Class for logical disks/mount points"""

    def __init__(self, system: 'System') -> None:
        self._system: System = system
        self._partitions: List['Partition'] = []
        self['Description'] = ""
        self['Device I.D.'] = ""
        self['Type'] = ""
        self['Filesystem'] = ""
        self['Free Space'] = 0
        self['Max Component Length'] = -1
        self['Name'] = ""
        self['Path'] = ""
        self['Size'] = 0
        self['Label'] = ''
        self['Serial'] = ""
        self['Mounted'] = ''

    def add_partition(self, partition: 'Partition') -> None:
        """Add a partition to this logical disk"""
        self._partitions.append(partition)

    def get_partitions(self) -> Tuple['Partition']:
        return tuple(self._partitions)

    def get_system(self) -> 'System':
        return self._system

    def __str__(self) -> str:
        return "Logical Disk -- " + ", ".join((
            "Path: " + self['Path'],
            'Label: ' + self['Label'],
            'Filesystem: ' + self['Filesystem'],
            'Free Space: ' + human_readable_units(self['Free Space'])
        ))


class Partition(SystemComponent):
    """Contains information about partitions. This includes logical disk,
    or 'volume' information. The same volume may span several disks, and the
    filesystem of the partition, will in those cases be the filesystem of the
    spanned volume. The partition may in that case not include a functional
    filesystem on its own, though its contents will be part of one.
    """

    def __init__(self, physical_disk: 'PhysicalDisk') -> None:
        self._physical_disk: 'PhysicalDisk' = physical_disk
        self._logical_disks: list['LogicalDisk'] = []
        self['Blocksize'] = -1
        self['Bootable'] = False
        self['Active'] = False
        self['Description'] = ""
        self['Path'] = ""
        self['Device I.D.'] = ""
        self['Disk Number'] = -1
        self['Partition Number'] = -1
        self['Blocks'] = -1
        self['Primary'] = False
        self['Size'] = 0
        self['Offset'] = -1
        self['Type'] = ""
        self.isdummy = False

    def add_logical_disk(self, logical_disk: 'LogicalDisk') -> None:
        """Set the logical disk connected to this partition."""
        new_logical_disk = True
        for each_logical_disk in self.get_logical_disks():
            if each_logical_disk['Device I.D.'] == logical_disk['Device I.D.']:
                new_logical_disk = False
        if new_logical_disk:
            self._logical_disks.append(logical_disk)

    def get_logical_disks(self) -> tuple['LogicalDisk']:
        return tuple(self._logical_disks)

    def get_physical_disk(self) -> 'PhysicalDisk':
        return self._physical_disk

    def __str__(self) -> str:
        """overloading the __str__ method"""
        partition = 'Partition -- ' + ", ".join((
            'ID: ' + self['Device I.D.'],
            'Type: ' + self['Type'],
            'Size: ' + human_readable_units(self['Size']),
            'Offset: ' + str(self['Offset'])
        ))
        logical_disks = [
            "\n".join([
                "  " + line
                for line in str(logical_disk).split("\n")
            ])
            for logical_disk in self.get_logical_disks()
        ]
        return "\n".join((partition, *logical_disks))


class DummyPartition(Partition):
    def __init__(self, disk: 'PhysicalDisk', logical_disk: 'LogicalDisk'):
        super().__init__(disk)
        self.isdummy = True
        self.add_logical_disk(logical_disk)

    def __str__(self) -> str:
        return str(self.get_logical_disks()[0])


class PhysicalDisk(SystemComponent):
    """Contains information about physical drives."""

    def __init__(self, system: SystemComponent) -> None:
        self._system = system
        self._partitions = []
        self['Size'] = 0
        self['Disk Number'] = -1
        self['Device I.D.'] = ""
        self['Path'] = ""
        self['Media'] = ""
        self['Serial'] = ""
        self['Model'] = ""
        self['Sectors'] = 0
        self['Heads'] = 0
        self['Cylinders'] = 0
        self['Bytes per Sector'] = 0
        self['Firmware'] = ""
        self['Interface'] = ""
        self['Media Loaded'] = False
        self['Status'] = ""

    def add_partition(self, partition: SystemComponent) -> None:
        """add a Partition object to the disk."""
        self._partitions.append(partition)

    def get_partitions(self) -> tuple:
        return tuple(self._partitions)

    def get_system(self) -> SystemComponent:
        return self._system

    def __str__(self) -> str:
        """Overloading the string method"""
        disk = 'Disk -- ' + ", ".join((
            "Disk Number: {}".format(self['Disk Number']),
            "Path: " + self['Path'],
            "Media: " + self['Media'],
            "Size: " + human_readable_units(self['Size'])
        ))
        partitions = ["\n".join(
                        ["  " + line for line in str(partition).split("\n")])
                      for partition in self.get_partitions()]
        return "\n".join((disk, *partitions, ""))
