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
from . human_readable_units import human_readable_units
from . system_component import SystemComponent


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
