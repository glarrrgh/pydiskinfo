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


def str_system(system: System) -> str:
    """Returns a string representation of the system consisting of the
    properties chosen on the command line."""
    return 'System -- ' + ', '.join((
        f'Name: {system["Name"]}',
        f'Type: {system["Type"]}',
        f'Version: {system["Version"]}'
    ))


def str_physical_disk(
    physical_disk: PhysicalDisk,
    arguments: SanitizedArguments
) -> str:
    """Returns a string representation of the physical disk consisting of the
    properties chosen on the command line."""
    properties = arguments.physical_disk_options
    strings = []
    for each_property in properties:
        if each_property == 'Size':
            if arguments.physical_disk_size_human_readable:
                size = human_readable_units(physical_disk['Size'])
            else:
                size = str(physical_disk['Size'])
            strings.append(
                f'Size: {size}'
            )
        else:
            strings.append(f'{each_property}: {str(physical_disk[each_property])}')
    return f'Physical Disk -- {", ".join(strings)}'


def str_partition(partition: Partition, arguments: SanitizedArguments) -> str:
    """Returns a string representation of the partition consisting of the
    properties chosen on the command line."""
    strings = []
    properties = arguments.partition_options
    for each_property in properties:
        if each_property == 'Size':
            if arguments.partition_size_human_readable:
                size = human_readable_units(partition['Size'])
            else:
                size = str(partition['Size'])
            strings.append(
                f'Size: {size}'
            )
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
            if arguments.logical_disk_size_human_readable:
                size = human_readable_units(logical_disk['Size'])
            else:
                size = str(logical_disk['Size'])
            strings.append(
                f'Size: {size}'
            )
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
