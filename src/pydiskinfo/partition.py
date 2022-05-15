"""pydiskinfo Partition class definition

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

import os
from xmlrpc.client import boolean
from typing import Tuple

from . human_readable_units import human_readable_units
from . system_component import SystemComponent


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
        partition = 'Partition -- ' + ", ".join(('ID: ' + self['Device I.D.'], 
                                               'Type: ' + self['Type'], 
                                               'Size: ' + human_readable_units(self['Size']), 
                                               'Offset: '+ str(self['Offset'])
                                               ))
        logical_disks = ["\n".join(["  " + line for line in str(logical_disk).split("\n")]) for logical_disk in self.get_logical_disks()] 
        return "\n".join((partition, *logical_disks))


class DummyPartition(Partition):
    def __init__(self, disk: 'PhysicalDisk', logical_disk: 'LogicalDisk'):
        super().__init__(disk)
        self.isdummy = True
        self.add_logical_disk(logical_disk)

    def __str__(self) -> str:
        return str(self.get_logical_disks()[0])
