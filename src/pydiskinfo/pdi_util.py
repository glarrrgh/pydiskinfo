"""A commandline program using the pydiskinfo module

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
from . argument_parsing import get_arguments, SanitizedArguments
from .system import System, create_system
from . human_readable_units import human_readable_units
from .physical_disk import PhysicalDisk
from .logical_disk import LogicalDisk
from .partition import Partition
from . system_component import SystemComponent


class Stringifier:
    def __init__(self, arguments: SanitizedArguments = None) -> None:
        self.arguments = arguments
        self.strings = []

    def convert_int_to_str(
        self,
        value: int,
        human_readable: bool = True
    ) -> str:
        """Return a string based on value. Human readable if """
        if human_readable:
            return human_readable_units(value)
        else:
            return str(value)


class SystemStringifier(Stringifier):
    def __init__(self, system: System) -> None:
        self.system = system

    def __str__(self) -> str:
        """Returns a string representation of the system consisting of the
        properties chosen on the command line."""
        return 'System -- ' + ', '.join((
            f'Name: {self.system["Name"]}',
            f'Type: {self.system["Type"]}',
            f'Version: {self.system["Version"]}'
        ))


class PhysicalDiskStringifier(Stringifier):
    def __init__(
        self,
        physical_disk: PhysicalDisk,
        arguments: SanitizedArguments
    ) -> None:
        super().__init__(arguments=arguments)
        self.physical_disk = physical_disk

    def __str__(self) -> str:
        """Returns a string representation of the physical disk consisting of the
        properties chosen on the command line."""

        strings = []
        for each_property in self.arguments.physical_disk_options:
            if each_property == 'Size':
                size = self.convert_int_to_str(
                    self.physical_disk['Size'],
                    self.arguments.physical_disk_size_human_readable
                )
                strings.append(f'Size: {size}')
            else:
                strings.append(
                    f'{each_property}: '
                    f'{str(self.physical_disk[each_property])}'
                )
        return f'Physical Disk -- {", ".join(strings)}'


class PartitionStringifier(Stringifier):
    def __init__(
        self,
        partition: Partition,
        arguments: SanitizedArguments
    ) -> None:
        super().__init__(arguments=arguments)
        self.partition = partition

    def __str__(self) -> str:
        """Returns a string representation of the physical disk consisting of the
        properties chosen on the command line."""
        strings = []
        for each_property in self.arguments.partition_options:
            if each_property == 'Size':
                size = self.convert_int_to_str(
                    self.partition['Size'],
                    self.arguments.partition_size_human_readable
                )
                strings.append(f'Size: {size}')
            else:
                strings.append(
                    f'{each_property}: {str(self.partition[each_property])}'
                )
        return f'Partition -- {", ".join(strings)}'


class LogicalDiskStringifier(Stringifier):
    def __init__(
        self,
        logical_disk: LogicalDisk,
        arguments: SanitizedArguments
    ) -> None:
        super().__init__(arguments=arguments)
        self.logical_disk = logical_disk

    def __str__(self) -> str:
        """Returns a string representation of the physical disk consisting of the
        properties chosen on the command line."""
        strings = []
        for each_property in self.arguments.logical_disk_options:
            if each_property == 'Size':
                size = self.convert_int_to_str(
                    self.logical_disk['Size'],
                    self.arguments.logical_disk_size_human_readable
                )
                strings.append(f'Size: {size}')
            elif each_property == 'Free Space':
                strings.append(
                    f'Free Space: '
                    f'{human_readable_units(self.logical_disk["Free Space"])}'
                )
            else:
                strings.append(
                    f'{each_property}: {str(self.logical_disk[each_property])}'
                )
        return f'Logical Disk -- {", ".join(strings)}'


def stringify(
    system_component: SystemComponent,
    arguments: SanitizedArguments = None
):
    result = None
    if isinstance(system_component, System):
        result = SystemStringifier(system=system_component)
    elif isinstance(system_component, PhysicalDisk):
        result = PhysicalDiskStringifier(
            physical_disk=system_component,
            arguments=arguments
        )
    elif isinstance(system_component, Partition):
        result = PartitionStringifier(
            partition=system_component,
            arguments=arguments
        )
    elif isinstance(system_component, LogicalDisk):
        result = LogicalDiskStringifier(
            logical_disk=system_component,
            arguments=arguments
        )
    return str(result)


class LineAssembler:
    def __init__(
        self,
        arguments: SanitizedArguments,
        system: System = None
    ) -> None:
        self.indent = 0
        self.arguments = arguments
        if system:
            self.system = system
        else:
            self.system = create_system(self.arguments.system_name)
        self.lines: list[str] = []
        self.create_itemlines()

    def add_item_line(self, item: SystemComponent) -> None:
        self.lines.append(
            f'{" " * self.indent}{stringify(item, self.arguments)}'
        )

    def create_itemlines(self) -> None:
        self.lines.append(stringify(self.system))
        self.indent = 2
        if self.arguments.list_from_partitions:
            self.create_partition_lines(self.system)
        elif self.arguments.logical_disk_orientation:
            self.create_disk_lines(components=self.system.get_logical_disks())
        else:
            self.create_disk_lines(components=self.system.get_physical_disks())

    def create_partition_lines(self, component: SystemComponent) -> None:
        if self.arguments.list_partitions:
            for each_partition in component.get_partitions():
                if not each_partition.isdummy:
                    self.add_item_line(each_partition)
                    self.indent += 2
                if self.arguments.partitions_list_children:
                    if self.arguments.logical_disk_orientation:
                        self.add_item_line(each_partition.get_physical_disk())
                    else:
                        for each_logical_disk in \
                                each_partition.get_logical_disks():
                            self.add_item_line(each_logical_disk)
                self.indent -= 2

    def create_disk_lines(self, components: list[SystemComponent]) -> None:
        for each_component in components:
            self.add_item_line(each_component)
            self.indent += 2
            self.create_partition_lines(each_component)
            self.indent -= 2

    def __str__(self) -> str:
        return '\n'.join(self.lines)


def main() -> None:
    arguments = get_arguments()
    if arguments:
        print(LineAssembler(arguments))
