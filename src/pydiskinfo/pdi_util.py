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


def create_item_line(
    indent: int,
    item: str,
    arguments: SanitizedArguments
) -> None:
    return f'{" " * indent}{stringify(item, arguments)}'


def create_partition_lines(
    indent: int,
    partitions: list,
    arguments: SanitizedArguments
) -> list[str]:
    lines = []
    if arguments.list_partitions:
        for each_partition in partitions:
            if not each_partition.isdummy:
                lines.append(create_item_line(
                    indent,
                    each_partition, arguments
                ))
                indent += 2
            if arguments.partitions_list_children:
                if arguments.logical_disk_orientation:
                    lines.append(create_item_line(
                        indent,
                        each_partition.get_physical_disk(),
                        arguments
                    ))
                else:
                    for each_logical_disk in \
                            each_partition.get_logical_disks():
                        lines.append(create_item_line(
                            indent,
                            each_logical_disk,
                            arguments
                        ))
            indent -= 2
    return lines


def create_disk_lines(
    indent: int,
    components: list[SystemComponent],
    arguments: SanitizedArguments
) -> list[str]:
    lines = []
    for each_component in components:
        lines.append(create_item_line(
            indent,
            each_component,
            arguments
        ))
        indent += 2
        lines.extend(create_partition_lines(
            indent,
            each_component.get_partitions(),
            arguments
        ))
        indent -= 2
    return lines


def create_itemlines(arguments: SanitizedArguments) -> str:
    lines = []
    system = create_system(arguments.system_name)
    lines.append(stringify(system))
    if arguments.list_from_partitions:
        lines.extend(create_partition_lines(
            indent=2,
            partitions=system.get_partitions(),
            arguments=arguments
        ))
    elif arguments.logical_disk_orientation:
        lines.extend(create_disk_lines(
            indent=2,
            components=system.get_logical_disks(),
            arguments=arguments
        ))
    else:
        lines.extend(create_disk_lines(
            indent=2,
            components=system.get_physical_disks(),
            arguments=arguments
        ))
    return '\n'.join(lines)


def main() -> None:
    arguments = get_arguments()
    if arguments:
        print(create_itemlines(arguments))
