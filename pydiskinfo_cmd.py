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
    return 'System: ' + ', '.join(( 
        'Name: {}'.format(system['Name']), 
        'Type: {}'.format(system['Type'])
    ))

def str_physical_disk(physical_disk: PhysicalDisk, properties: str) -> str:
    strings = []
    sanitized_properties = [property for property in properties if property in set(properties)]
    for each_property in sanitized_properties:
        if each_property == 's':
            strings.append(human_readable_units(physical_disk['Size']))
        elif each_property == 'S':
            strings.append(physical_disk['Size'])
    return 'Physical Disk:' + ', '.join(strings)

def str_partition(partition: Partition) -> str:
    return 'Partition: ' + ', '.join((
        '',
    ))

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
Default: -pp Ldtse

    L   List logical disks under each partition. The logical disk properties 
        will be listed according to the -lp option.
    D   Show the physical disk the partition is part of. 
    b   Show blocksize.
    B   Show if partition is bootable.
    o   Show if partition is the active boot partition.
    D   Show a description created by the system.
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
Default: -lp pVtfF

    P   List partitions that make up each logical disk. Ignored unless -l is 
        specified. 
    x   Show a description created by the system.
    d   Show the system device I.D.
    t   Show some type information ablut the logical disk.
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
, formatter_class=argparse.RawDescriptionHelpFormatter
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
        default='Ldtse',
        help="Partition disk properties to include in output"
    )
    argument_parser.add_argument(
        '-lp',
        type=str,
        default='pVtfF',
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
        help='''Start listing from a logical disk viewpoint. Remember to add P 
to the -lp option to list partition under each logical disk. If included in the 
parameter list (-lp, and -pp), the partitions will be listed as part of a 
logical disk, and the physical disk the partitions are part of. So pretty much 
the reverse of normal behaviour.
    
'''
    )
    argument_parser.add_argument(
        '-n',
        type=str,
        help='Add a system name, if you need to differentiate between outputs.'
    )
    args = argument_parser.parse_args()
    system = System()
    print(str(system))

if __name__ == '__main__':
    main()
