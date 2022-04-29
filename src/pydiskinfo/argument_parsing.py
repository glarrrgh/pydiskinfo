from argparse import ArgumentParser, RawTextHelpFormatter


def get_arguments() -> dict:
    argument_parser = ArgumentParser(
        description="""List system block devices.

The default behaviour is to list all devices from the system down trough
physical disk and partitions, to logical disks. The partitions are only
"physical" partitions. That means that they are part of a physical disk, and
not part of a volume manager device. And logical disks will not show all
volumes in the system. Only those that are on a physical disk. Network volumes,
for instance, will not show up in the listings. """,
        epilog="""Physical disk properties:
Combine the corresponding characters in a string after the -dp option. Order
will be kept according to the string, except for the partition list.
Default: -dp Pipts

    P   List partitions under each disk. The partition properties will be
        listed according to the -pp option.
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
""",
        formatter_class=RawTextHelpFormatter
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
        help=(
            '''Start listing from a logical disk viewpoint. Remember to add P to
the -lp option to list partition under each logical disk. If
included in the parameter list (-lp, and -pp), the partitions
will be listed as part of a logical disk, and the physical disk
the partitions are part of. So pretty much the reverse of
normal behaviour.
''')
    )
    argument_parser.add_argument(
        '-n',
        type=str,
        help='Add a system name, if you need to differentiate between outputs.'
    )
    return vars(argument_parser.parse_args())
