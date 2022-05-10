from argparse import ArgumentParser, RawTextHelpFormatter


class DisplayItem:
    tokens: dict = {
        'P': 'physical_disk_list_partitions',
        's': 'Size',
        'S': 'Size',
        'i': 'Disk Number',
        'd': 'Device I.D.',
        'p': 'Path',
        't': 'Media',
        'n': 'Serial',
        'm': 'Model',
        'c': 'Sectors',
        'h': 'Heads',
        'C': 'Cylinders',
        'f': 'Firmware',
        'I': 'Interface',
        'M': 'Media Loaded',
        'a': 'Status'
    }

    def __init__(self, token: str) -> None:
        self.key = self.tokens[token]


class SanitizedArguments:
    def __init__(self, arguments: dict = None) -> None:
        self.list_partitions = False
        self.partitions_list_children = False
        if not arguments:
            arguments = {}
        try:
            self.logical_disk_orientation = arguments['l']
        except KeyError:
            self.logical_disk_orientation = False
        try:
            (
                self.physical_disk_options,
                physical_disk_list_partitions,
                self.physical_disk_size_human_readable
            ) = self._parse_dp(arguments['dp'])
        except KeyError:
            self.physical_disk_options = []
            physical_disk_list_partitions = False
            self.physical_disk_size_human_readable = False
        try:
            (
                self.partition_options,
                partition_list_logical_disks,
                partition_show_physical_disk,
                self.partition_size_human_readable
            ) = self._parse_pp(arguments['pp'])
        except KeyError:
            self.partition_options = []
            partition_list_logical_disks = False
            partition_show_physical_disk = False
            self.partition_size_human_readable = False
        try:
            (
                self.logical_disk_options,
                logical_disk_list_partitions,
                self.logical_disk_size_human_readable
            ) = self._parse_lp(arguments['lp'])
        except KeyError:
            self.logical_disk_options = []
            logical_disk_list_partitions = False
            self.logical_disk_size_human_readable = False
        try:
            self.list_from_partitions = arguments['p']
        except KeyError:
            self.list_from_partitions = False
        try:
            if arguments['n']:
                self.system_name = arguments['n']
            else:
                self.system_name = ''
        except KeyError:
            self.system_name = ''
        if self.logical_disk_orientation and logical_disk_list_partitions:
            self.list_partitions = True
        elif not self.logical_disk_orientation \
                and physical_disk_list_partitions:
            self.list_partitions = True
        if self.list_from_partitions:
            self.list_partitions = True
        if partition_list_logical_disks and not self.logical_disk_orientation:
            self.partitions_list_children = True
        elif partition_show_physical_disk and self.logical_disk_orientation:
            self.partitions_list_children = True

    def _add_to_list(self, some_list: list, item: str) -> None:
        if item not in some_list:
            some_list.append(item)

    def _parse_dp(self, arguments: str) -> tuple:
        size_human_readable = False
        list_partitions = False
        return_list = []
        for each_option in arguments:
            if each_option == 'P':
                list_partitions = True
            elif each_option == 's':
                self._add_to_list(return_list, 'Size')
                size_human_readable = True
            elif each_option == 'S':
                self._add_to_list(return_list, 'Size')
                size_human_readable = False
            elif each_option == 'i':
                self._add_to_list(return_list, 'Disk Number')
            elif each_option == 'd':
                self._add_to_list(return_list, 'Device I.D.')
            elif each_option == 'p':
                self._add_to_list(return_list, 'Path')
            elif each_option == 't':
                self._add_to_list(return_list, 'Media')
            elif each_option == 'n':
                self._add_to_list(return_list, 'Serial')
            elif each_option == 'm':
                self._add_to_list(return_list, 'Model')
            elif each_option == 'c':
                self._add_to_list(return_list, 'Sectors')
            elif each_option == 'b':
                self._add_to_list(return_list, 'Bytes per Sector')
            elif each_option == 'h':
                self._add_to_list(return_list, 'Heads')
            elif each_option == 'C':
                self._add_to_list(return_list, 'Cylinders')
            elif each_option == 'f':
                self._add_to_list(return_list, 'Firmware')
            elif each_option == 'I':
                self._add_to_list(return_list, 'Interface')
            elif each_option == 'M':
                self._add_to_list(return_list, 'Media Loaded')
            elif each_option == 'a':
                self._add_to_list(return_list, 'Status')

        return return_list, list_partitions, size_human_readable

    def _parse_pp(self, arguments: str) -> tuple:
        size_human_readable = False
        list_logical_disks = False
        show_physical_disk = False
        return_list = []
        for each_option in arguments:
            if each_option == 'L':
                list_logical_disks = True
            elif each_option == 'D':
                show_physical_disk = True
            elif each_option == 'b':
                self._add_to_list(return_list, 'Blocksize')
            elif each_option == 'B':
                self._add_to_list(return_list, 'Bootable')
            elif each_option == 'o':
                self._add_to_list(return_list, 'Active')
            elif each_option == 'x':
                self._add_to_list(return_list, 'Description')
            elif each_option == 'p':
                self._add_to_list(return_list, 'Path')
            elif each_option == 'd':
                self._add_to_list(return_list, 'Device I.D.')
            elif each_option == 'i':
                self._add_to_list(return_list, 'Disk Number')
            elif each_option == 'N':
                self._add_to_list(return_list, 'Partition Number')
            elif each_option == 'c':
                self._add_to_list(return_list, 'Blocks')
            elif each_option == 'r':
                self._add_to_list(return_list, 'Primary')
            elif each_option == 's':
                self._add_to_list(return_list, 'Size')
                size_human_readable = True
            elif each_option == 'S':
                self._add_to_list(return_list, 'Size')
                size_human_readable = False
            elif each_option == 'e':
                self._add_to_list(return_list, 'Offset')
            elif each_option == 't':
                self._add_to_list(return_list, 'Type')

        return (
            return_list,
            list_logical_disks,
            show_physical_disk,
            size_human_readable
        )

    def _parse_lp(self, arguments: str) -> tuple:
        size_human_readable = False
        list_partitions = False
        return_list = []
        for each_option in arguments:
            if each_option == 'P':
                list_partitions = True
            elif each_option == 'x':
                self._add_to_list(return_list, 'Description')
            elif each_option == 'd':
                self._add_to_list(return_list, 'Device I.D.')
            elif each_option == 't':
                self._add_to_list(return_list, 'Type')
            elif each_option == 'f':
                self._add_to_list(return_list, 'Filesystem')
            elif each_option == 'F':
                self._add_to_list(return_list, 'Free Space')
            elif each_option == 'U':
                self._add_to_list(return_list, 'Max Component Length')
            elif each_option == 'v':
                self._add_to_list(return_list, 'Name')
            elif each_option == 'M':
                self._add_to_list(return_list, 'Mounted')
            elif each_option == 'p':
                self._add_to_list(return_list, 'Path')
            elif each_option == 's':
                self._add_to_list(return_list, 'Size')
                size_human_readable = True
            elif each_option == 'S':
                self._add_to_list(return_list, 'Size')
                size_human_readable = False
            elif each_option == 'V':
                self._add_to_list(return_list, 'Label')
            elif each_option == 'n':
                self._add_to_list(return_list, 'Serial')

        return (
            return_list,
            list_partitions,
            size_human_readable
        )


def get_arguments() -> SanitizedArguments:
    argument_parser = ArgumentParser(
        description="""List system block devices.

The default behaviour is to list all devices from the system down through
physical disk and partitions, to logical disks. The partitions are only
"physical" partitions. That means that they are part of a physical disk, and
not part of a volume manager device. And logical disks will not show all
volumes in the system. Only those that are on a physical disk. Network volumes,
for instance, will not show up in the listings. """,
        epilog="""Physical disk properties:
Combine the corresponding characters in a string after the -dp option. Order
will be kept according to the string, except for the partition list.
Default: -dp Piptns

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
    b   Show bytes per sector. This is a good indication for block size.
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
Default: -lp PVfF

    P   List partitions that make up each logical disk. Ignored unless -l is
        specified.
    x   Show a description created by the system.
    d   Show the system device I.D.
    t   Show some type information about the logical disk.
    f   Show filesystem type in text.
    F   Show free space on the partition, if available. If it is 0, this
        information was probably not available.
    U   Show the maximum component lengt or path lenght on the filesystem.
    v   Show logical disk name.
    M   Show mounted Path (first available)
    p   Will show a raw access path, if available. If blank, you will have to
        do this via the partition
    s   Show size in human readable format.
    S   Show size in bytes.
    V   Show volume label.
    n   Show volume serial number.
""",
        formatter_class=RawTextHelpFormatter,
        exit_on_error=False
    )
    argument_parser.add_argument(
        '-dp',
        type=str,
        default='Piptns',
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
        default='PVfF',
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
    try:
        parsed_arguments = argument_parser.parse_args()
    except SystemExit:
        return None
    return SanitizedArguments(vars(parsed_arguments))
