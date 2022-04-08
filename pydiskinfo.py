"""A module for getting information about block devices in a system.

The pydiskinfo module is not a replacement for modules that gain file or 
filesystem information. It is mostly a supplement, for those rare situations 
when you need to know more about the physical devices rather than the 
filesystems and files on them. I made the module because I needed path 
information to do raw read off of hard drives. If other uses arise, I may be 
compelled to extend the module.

The module depends on the wmi module, when run on a windows system. No
extra modules need to be installed on linux systems. The linux functionality 
depends heavily on udev, so it will probably not work on other unix like 
systems. 

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

from pydiskinfo_system import System


if __name__ == "__main__":
    import argparse
    argument_parser = argparse.ArgumentParser(
description="List system block devices.", 
epilog="""
Physical disk properties:
Combine the corresponding character in a string after the -dp option. Order will 
be kept according to the string, except for the partition list.
Default: -dp Pipts

    P   List partitions under each disk. The partition properties will be listed 
        according to the -pp option.
    s   Show size in human readable format.
    S   Show size in bytes.
    i   Show system disk number.
    d   Show the system device ID.
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
Combine the corrseponding character in a string after the -dp option. Order will 
be kept according to the string, except for the logical disk list.

    
"""
, formatter_class=argparse.RawDescriptionHelpFormatter
)
    argument_parser.add_argument(   
        '-dp', 
        type=str, 
        help='Physical disk properties to include in output')
    argument_parser.add_argument(
        '-pp',
        type=str,
        help="Partition disk properties to include in output"
    )
    args = argument_parser.parse_args()
    system = System()
    print(str(system))
