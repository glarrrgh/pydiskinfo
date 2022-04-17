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

import argparse

from pydiskinfo import System, PhysicalDisk, Partition, LogicalDisk
from human_readable_units import human_readable_units

def str_system(system: System) -> str:
    """Returns a string representation of the system consisting of the 
    properties chosen on the command line."""
    return 'System: ' + ', '.join(( 
        f'Name: {system["Name"]}', 
        f'Type: {system["Type"]}',
        f'Version: {system["Version"]}'
    ))

def str_physical_disk(physical_disk: PhysicalDisk, properties: str) -> str:
    """Returns a string representation of the physical disk consisting of the 
    properties chosen on the command line."""
    strings = []
    sanitized_properties = [property for property in properties if property in set(properties)]
    for each_property in sanitized_properties:
        if each_property == 's':
            strings.append(f'Size: {human_readable_units(physical_disk["Size"])}')
        elif each_property == 'S':
            strings.append(f'Size: {physical_disk["Size"]}')
        elif each_property == 'i':
            strings.append(f'Disk Number: {physical_disk["Disk Number"]}')
        elif each_property == 'd':
            strings.append(f'Device I.D.: {physical_disk["Device I.D."]}')
        elif each_property == 'p':
            strings.append(f'Path: {physical_disk["Path"]}')
        elif each_property == 't':
            strings.append(f'Media Type: {physical_disk["Media Type"]}')
        elif each_property == 'n':
            strings.append(f'Serical Number: {physical_disk["Serial Number"]}')
        elif each_property == 'm':
            strings.append(f'Model: {physical_disk["Model"]}')
        elif each_property == 'c':
            strings.append(f'Sectors: {physical_disk["Sectors"]}')
        elif each_property == 'b':
            strings.append(f'Bytes per Sector: {physical_disk["Bytes per Sector"]}')
        elif each_property == 'h':
            strings.append(f'Heads: {physical_disk["Heads"]}')
        elif each_property == 'C':
            strings.append(f'Cylinders: {physical_disk["Cylinders"]}')
        elif each_property == 'f':
            strings.append(f'Firmware: {physical_disk["Firmware Version"]}')
        elif each_property == 'I':
            strings.append(f'Interface Type: {physical_disk["Interface Type"]}')
        elif each_property == 'M':
            strings.append(f'Media is {"" if physical_disk["Media Loaded"] else "not "}Loaded')
        elif each_property == 'a':
            strings.append(f'Status: {physical_disk["Status"]}')
    return 'Physical Disk: ' + ', '.join(strings)

def str_partition(partition: Partition, properties: str) -> str:
    """Returns a string representation of the partition consisting of the 
    properties chosen on the command line."""
    strings = []
    sanitized_properties = [property for property in properties if property in set(properties)]
    for each_property in sanitized_properties:
        if each_property == 'b':
            strings.append(f'Blocksize: {partition["Blocksize"]}')
        elif each_property == 'B':
            strings.append(f'is {"" if partition["Bootable"] else "not "}bootable')
        elif each_property == 'o':
            strings.append(f'is {"" if partition["Boot Partition"] else "not "}the active boot partition')
        elif each_property == 'x':
            strings.append(f'Description: {partition["Description"]}')
        elif each_property == 'p':
            strings.append(f'Path: {partition["Path"]}')
        elif each_property == 'd':
            strings.append(f'Device I.D.: {partition["Device I.D."]}')
        elif each_property == 'i':
            strings.append(f'Disk Number: {partition["Disk Number"]}')
        elif each_property == 'N':
            strings.append(f'Partition Number: {partition["Partition Number"]}')
        elif each_property == 'c':
            strings.append(f'Blocks: {partition["Number of Blocks"]}')
        elif each_property == 'r':
            strings.append(f'is {"" if partition["Primary Partition"] else "not "}a primary partition')
        elif each_property == 's':
            strings.append(f'Size: {human_readable_units(partition["Size"])}')
        elif each_property == 'S':
            strings.append(f'Size: {partition["Size"]}')
        elif each_property == 'e':
            strings.append(f'Offset: {partition["Starting Offset"]}')
        elif each_property == 't':
            strings.append(f'Type: {partition["Type"]}')
    return 'Partition: ' + ', '.join(strings)

def str_logical_disk(logical_disk: LogicalDisk, properties: str) -> str:
    """Returns a string representation of the logical disk consisting of the 
    properties chosen on the command line."""
    strings = []
    sanitized_properties = [property for property in properties if property in set(properties)]
    for each_property in sanitized_properties:
        if each_property == 'x':
            strings.append(f'Description: {logical_disk["Description"]}')
        elif each_property == 'd':
            strings.append(f'Device I.D.: {logical_disk["Device I.D."]}')
        elif each_property == 't':
            strings.append(f'Type: {logical_disk["Drive Type"]}')
        elif each_property == 'f':
            strings.append(f'File System: {logical_disk["File System"]}')
        elif each_property == 'F':
            strings.append(f'Free Space: {human_readable_units(logical_disk["Free Space"])}')
        elif each_property == 'U':
            strings.append(f'Max Component Length: {logical_disk["Maximum Component Length"]}')
        elif each_property == 'v':
            strings.append(f'Logical Disk Name: {logical_disk["Name"]}')
        elif each_property == 'p':
            strings.append(f'Path: {logical_disk["Path"]}')
        elif each_property == 's':
            strings.append(f'Size: {human_readable_units(logical_disk["Size"])}')
        elif each_property == 'S':
            strings.append(f'Size: {logical_disk["Size"]}')
        elif each_property == 'V':
            strings.append(f'Volume Name: {logical_disk["Volume Name"]}')
        elif each_property == 'n':
            strings.append(f'Volume Serial Number: {logical_disk["Volume Serial Number"]}')
    return 'Logical Disk: ' + ', '.join(strings)


def main():
    argument_parser = argparse.ArgumentParser(
description="""List system block devices. 

The default behaviour is to list all devices from the system down trough 
physical disk and partitions, to logical disks. The partitions are only 
"physical" partitions. That means that they are part of a physical disk, and not 
part of a volume manager device. And logical disks will not show all volumes in 
the system. Only those that are on a physical disk. Network volumes, for 
instance, will not show up in the listings. 
""", 
epilog="""
Physical disk properties:
Combine the corresponding characters in a string after the -dp option. Order will 
be kept according to the string, except for the partition list.
Default: -dp Pipts

    P   List partitions under each disk. The partition properties will be listed 
        according to the -pp option.
    s   Show size in human readable format.
    S   Show size in bytes.
    i   Show system disk number.
    d   Show the system device I.D.
    p   Show a path usable for raw access.
    t   Show media type as repported by the system.
    n   Show device serial number.
    m   Show model of device as registered by the system.
    c   Show number of sectors as repported by the system.
    b   Show bytes per sector. This is a good guide for block size.
    h   Show number of heads.
    C   Show number of cylinders.
    f   Show firmware version.
    I   Show interface type.
    M   Show if media is loaded.
    a   Show device status.

Partition properties:
Combine the corrseponding characters in a string after the -pp option. Order 
will be kept according to the string, except for the logical disk list.
Default: -pp LDdtse

    L   List logical disks under each partition. The logical disk properties 
        will be listed according to the -lp option.
    D   Show the physical disk the partition is part of. Ignored unless -l is 
        specified.
    b   Show blocksize.
    B   Show if partition is bootable.
    o   Show if partition is the active boot partition.
    x   Show a description created by the system.
    p   Show a path usable for raw access. Not usable in windows. Use the 
        physical disk and read <size> bytes from <starting offset> in stead.
    d   Show the system device I.D.
    i   Show the disk number that the partition is located on.
    N   Show the partition number on the physical disk.
    c   Show number of blocks.
    r   Show if the partition is a primary partition.
    s   Show size in human readable format.
    S   Show size in bytes.
    e   Show starting offset on physical disk in bytes.
    t   Show partition type. On windows this will be some interpretation of 
        usage in the system. On linux this will be the partition type as text.

Logical disk properties:
Combine the corresponding characters in a string after the -lp option. Order 
will be kept according to the string, except for the partition list.
Default: -lp PpVtfF

    P   List partitions that make up each logical disk. Ignored unless -l is 
        specified. 
    x   Show a description created by the system.
    d   Show the system device I.D.
    t   Show some type information about the logical disk.
    f   Show filesystem in text.
    F   Show free space on the partition, if available. If it is 0, this 
        information was probably not available.
    U   Show the maximum component lengt or path lenght on the filesystem.
    v   Show logical disk name.
    p   Show a path usable for raw access. Will show the regular access path in 
        windows. On windows you will have to read each physical disk and use 
        partition <size> and <starting offset> to get the raw access.
    s   Show size in human readable format.
    S   Show size in bytes.
    V   Show volume name. For instance the volume label.
    n   Show volume serial number. 
"""
, formatter_class=argparse.RawTextHelpFormatter
)
    argument_parser.add_argument(   
        '-dp', 
        type=str, 
        default='Pipts',
        help='Physical disk properties to include in output'
    )
    argument_parser.add_argument(
        '-pp',
        type=str,
        default='LDdtse',
        help="Partition disk properties to include in output"
    )
    argument_parser.add_argument(
        '-lp',
        type=str,
        default='PpVtfF',
        help='Logical disk properties to include in output'
    )
    argument_parser.add_argument(
        '-p',
        action='store_true',
        help='Start listing from partitions, ignoring physical disks.'
    )
    argument_parser.add_argument(
        '-l',
        action='store_true',
        help=
'''Start listing from a logical disk viewpoint. Remember to add P to 
the -lp option to list partition under each logical disk. If 
included in the parameter list (-lp, and -pp), the partitions 
will be listed as part of a logical disk, and the physical disk 
the partitions are part of. So pretty much the reverse of 
normal behaviour.    
'''
    )
    argument_parser.add_argument(
        '-n',
        type=str,
        help='Add a system name, if you need to differentiate between outputs.'
    )
    args = vars(argument_parser.parse_args())
    system = System()
    print(str_system(system))
    if args['l']:
        for each_logical_disk in system['Logical Disks']:
            print(f'  {str_logical_disk(each_logical_disk, args["lp"])}')
            if 'P' in args['lp']:
                for each_partition in each_logical_disk['Partitions']:
                    if not each_partition.isdummy:
                        print(f'    {str_partition(each_partition, args["pp"])}')
                        indentation = '      '
                    else:
                        indentation = '    '
                    if 'D' in args['pp']:
                        print(f'{indentation}{str_physical_disk(each_partition["Physical Disk"], args["dp"])}')
    else:
        for each_physical_disk in system['Physical Disks']:
            print(f'  {str_physical_disk(each_physical_disk, args["dp"])}')
            if 'P' in args['dp']:
                for each_partition in each_physical_disk["Partitions"]:
                    if not each_partition.isdummy:
                        print(f'    {str_partition(each_partition, args["pp"])}')
                        indentation = '      '
                    else:
                        indentation = '    '
                    if 'L' in args['pp']:
                        for each_logical_disk in each_partition["Logical Disks"]:
                            print(f'{indentation}{str_logical_disk(each_logical_disk, args["lp"])}')
if __name__ == '__main__':
    main()
