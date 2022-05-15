"""pydiskinfo LogicalDisk class definition

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

from typing import List, Tuple, TYPE_CHECKING
from . human_readable_units import human_readable_units
from . system_component import SystemComponent
#if TYPE_CHECKING:
from . import System


class LogicalDisk(SystemComponent):
    """Class for logical disks/mount points"""

    def __init__(self, system: System) -> None:
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

    def get_system(self) -> System:
        return self._system

    def __str__(self) -> str:
        return "Logical Disk -- " + ", ".join((
            "Path: " + self['Path'],
            'Label: ' + self['Label'],
            'Filesystem: ' + self['Filesystem'],
            'Free Space: ' + human_readable_units(self['Free Space'])
        ))
