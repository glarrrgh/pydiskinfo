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


class Stringifyer:
    def __init__(self, arguments: SanitizedArguments = None) -> None:
        self.arguments = arguments

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


class SystemStringifyer(Stringifyer):
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


class PhysicalDiskStringifyer(Stringifyer):
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
                    f'{each_property}: {str(self.physical_disk[each_property])}'
                )
        return f'Physical Disk -- {", ".join(strings)}'


class PartitionStringifyer(Stringifyer):
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


class LogicalDiskStringifyer(Stringifyer):
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
    arguments: SanitizedArguments
):
    if isinstance(system_component, System):
        return SystemStringifyer(system=system_component)
    elif isinstance(system_component, PhysicalDisk):
        return PhysicalDiskStringifyer(
            physical_disk=system_component,
            arguments=arguments
        )
    elif isinstance(system_component, Partition):
        return PartitionStringifyer(
            partition=system_component,
            arguments=arguments
        )
    elif isinstance(system_component, LogicalDisk):
        return LogicalDiskStringifyer(
            logical_disk=system_component,
            arguments=arguments
        )
    else:
        return None


def str_system(system: System) -> str:
    """Returns a string representation of the system consisting of the
    properties chosen on the command line."""
    return 'System -- ' + ', '.join((
        f'Name: {system["Name"]}',
        f'Type: {system["Type"]}',
        f'Version: {system["Version"]}'
    ))


def convert_int_to_str(value: int, human_readable: bool = True) -> str:
    """Return a string based on value. Human readable if """
    if human_readable:
        return human_readable_units(value)
    else:
        return str(value)


def str_physical_disk(
    physical_disk: PhysicalDisk,
    arguments: SanitizedArguments
) -> str:
    """Returns a string representation of the physical disk consisting of the
    properties chosen on the command line."""
    strings = []
    for each_property in arguments.physical_disk_options:
        if each_property == 'Size':
            size = convert_int_to_str(
                physical_disk['Size'],
                arguments.physical_disk_size_human_readable    
            )
            strings.append(f'Size: {size}')
        else:
            strings.append(
                f'{each_property}: {str(physical_disk[each_property])}'
            )
    return f'Physical Disk -- {", ".join(strings)}'


def str_partition(partition: Partition, arguments: SanitizedArguments) -> str:
    """Returns a string representation of the partition consisting of the
    properties chosen on the command line."""
    strings = []
    properties = arguments.partition_options
    for each_property in properties:
        if each_property == 'Size':
            size = convert_int_to_str(
                partition['Size'],
                arguments.partition_size_human_readable
            )
            strings.append(f'Size: {size}')
        else:
            strings.append(f'{each_property}: {str(partition[each_property])}')
    return 'Partition -- ' + ', '.join(strings)


def str_logical_disk(
    logical_disk: LogicalDisk,
    arguments: SanitizedArguments
) -> str:
    """Returns a string representation of the logical disk consisting of the
    properties chosen on the command line."""
    strings = []
    properties = arguments.logical_disk_options
    for each_property in properties:
        if each_property == 'Size':
            size = convert_int_to_str(
                logical_disk['Size'],
                arguments.logical_disk_size_human_readable
            )
            strings.append(f'Size: {size}')
        elif each_property == 'Free Space':
            strings.append(
                f'Free Space: '
                f'{human_readable_units(logical_disk["Free Space"])}'
            )
        else:
            strings.append(
                f'{each_property}: {str(logical_disk[each_property])}'
            )
    return 'Logical Disk -- ' + ', '.join(strings)


def main() -> None:
    arguments = get_arguments()
    if arguments:
        system = create_system(arguments.system_name)
        print(str_system(system))
        if arguments.logical_disk_orientation:
            indent = 2
            if not arguments.list_from_partitions:
                for each_logical_disk in system.get_logical_disks():
                    logical_disk_string = str_logical_disk(
                        each_logical_disk,
                        arguments
                    )
                    print(
                        f'{" "*indent}{logical_disk_string}'
                    )
                    indent += 2
                    if arguments.logical_disk_list_partitions:
                        for each_partition in each_logical_disk.get_partitions():
                            if not each_partition.isdummy:
                                print(
                                    f'{" "*indent}'
                                    f'{str_partition(each_partition, arguments)}'
                                )
                                indent += 2
                            if arguments.partition_show_physical_disk:
                                physical_disk_string = str_physical_disk(
                                    each_partition.get_physical_disk(),
                                    arguments
                                )
                                print(
                                    f'{" "*indent}{physical_disk_string}'
                                )
                            indent -= 2
                    indent -= 2
            else:
                for each_partition in system.get_partitions():
                    print(
                        f'{" "*indent}'
                        f'{str_partition(each_partition, arguments)}'
                    )
                    indent += 2
                    if arguments.partition_show_physical_disk:
                        physical_disk_string = str_physical_disk(
                            each_partition.get_physical_disk(),
                            arguments
                        )
                        print(
                            f'{" "*indent}{physical_disk_string}'
                        )
                    indent -= 2
        else:
            indent = 2
            if not arguments.list_from_partitions:
                for each_physical_disk in system.get_physical_disks():
                    physical_disk_string = str_physical_disk(
                        each_physical_disk,
                        arguments
                    )
                    print(f'{" "*indent}{physical_disk_string}')
                    indent += 2
                    if arguments.physical_disk_list_partitions:
                        for each_partition in (
                            each_physical_disk
                            .get_partitions()
                        ):
                            if not each_partition.isdummy:
                                partition_string = str_partition(
                                    each_partition,
                                    arguments
                                )
                                print(f'{" "*indent}{partition_string}')
                                indent += 2
                            if arguments.partition_list_logical_disks:
                                for each_logical_disk in \
                                        each_partition.get_logical_disks():
                                    logical_disk_string = str_logical_disk(
                                        each_logical_disk,
                                        arguments
                                    )
                                    print(f'{" "*indent}{logical_disk_string}')
                            indent -= 2
                    indent -= 2
            else:
                for each_partition in system.get_partitions():
                    print(f'{" "*indent}{str_partition(each_partition, arguments)}')
                    indent += 2
                    if arguments.partition_list_logical_disks:
                        for each_logical_disk in each_partition.get_logical_disks():
                            logical_disk_string = str_logical_disk(
                                each_logical_disk,
                                arguments
                            )
                            print(f'{" "*indent}{logical_disk_string}')
                    indent -= 2
