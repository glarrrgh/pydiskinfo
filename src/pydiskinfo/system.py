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
from . physical_disk import PhysicalDisk
from . partition import Partition
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
