from asyncio import subprocess
import os
import re
try:
    import platform
except ModuleNotFoundError:
    platform = None
try:
    import distro
except ModuleNotFoundError:
    distro = None
from . import System
from . import PhysicalDisk
from . import PyDiskInfoParseError
from . import Partition
from . import LogicalDisk
from . import SystemComponent
from . partition import DummyPartition


class LinuxSystem(System):
    """This is the linux version of the System class.

    This class will take care of the special cases for when the module is
    running on linux systems. The availability of certain files and tools
    differ between linux distros and versions. Some info may be available
    as a regular user under some circumstances. But to get the module to
    find all variables, you will probably have to run in with raised
    privileges.

    """

    def __init__(self, name: str = None) -> None:
        super().__init__(name)
        self._set_version()

    def _set_version(self):
        """The distribution version of the system.

        There is no 'one' way to get version information about a linux distro.
        Kernel version would be easier, but is not really of any interest in
        the scope of the pydiskinfo module. So we do as best we can, and
        default to kernel version if all else fails."""
        if distro:
            self['Version'] = f'{distro.name()} {distro.version()}'
        elif platform:
            try:
                self['Version'] = platform.linux_distribution()
            except AttributeError:
                try:
                    self['Version'] = platform.dist()
                except AttributeError:
                    self['Version'] = f'{os.uname()[0]} {os.uname()[2]}'
        else:
            self['Version'] = f'{os.uname()[0]} {os.uname()[2]}'

    def _parse_system(self) -> None:
        block_devices = []
        try:
            with open('/proc/partitions', 'r') as proc_partitions:
                for each_line in proc_partitions:
                    match = re.match(
                        r'\s*(\d+)\s+(\d+)\s+(\d+)\s+(\w+)\s*',
                        each_line
                    )
                    if match:
                        block_devices.append(match.group(1, 2, 3, 4))
        except FileNotFoundError as err:
            raise PyDiskInfoParseError(
                'Missing /proc/partitions. Giving up parsing.'
            ) from err
        for each_device in block_devices:
            # handeling scsi hard drives
            if each_device[0] in ('8'):
                if not int(each_device[1]) // 16:
                    self['Physical Disks'].append(
                        LinuxPhysicalDisk(
                            self,
                            int(each_device[0]),
                            int(each_device[1]),
                            int(each_device[2]),
                            each_device[3]
                        )
                    )
            # handeling metadisk (raid) devices
            elif each_device[0] == '9':
                # read from /proc/mdstat
                self['Physical Disks'].append(
                    LinuxPhysicalDisk(
                        self,
                        int(each_device[0]),
                        int(each_device[1]),
                        int(each_device[2]),
                        each_device[3]
                    )
                )
        for each_device in block_devices:
            if int(each_device[1]) > 0:
                disk = None
                for each_disk in self['Physical Disks']:
                    if str(each_disk['Major Number']) == each_device[0]:
                        disk = each_disk
                        break
                partition = LinuxPartition(
                    disk,
                    int(each_device[0]),
                    int(each_device[1]),
                    int(each_device[2]),
                    each_device[3]
                )
                disk.add_partition(partition)
                self['Partitions'].append(partition)
        logical_disks = []
        try:
            mounts = subprocess.run(
                (
                    'df',
                    '--output=source,fstype,size,avail,target',
                    '--local',
                    '--block-size=1'
                ),
                capture_output=True,
                text=True
            )
            for each_line in mounts.stdout.split('\n'):
                match = re.search(
                    r'(.*\w)\s+(\w+)\s+(\d+)\s+(\d+)\s+(\/.*)',
                    each_line
                )
                if match:
                    logical_disks.append(match.groups())
        except OSError as err:
            raise PyDiskInfoParseError('Cant find the "df" command.') from err
        for each_logical_disk in logical_disks:
            logical_disk = LinuxLogicalDisk(
                self,
                each_logical_disk[4],
                each_logical_disk[1],
                int(each_logical_disk[2]),
                int(each_logical_disk[3])
            )
            for each_partition in self['Partitions']:
                if each_partition['Path'] == each_logical_disk[0]:
                    checked_logical_disk = self._add_logical_disk(logical_disk)
                    each_partition.add_logical_disk(checked_logical_disk)
                    checked_logical_disk.add_partition(each_partition)
            for each_disk in self['Physical Disks']:
                if each_disk['Path'] == each_logical_disk[0]:
                    checked_logical_disk = self._add_logical_disk(logical_disk)
                    dummy_partition = DummyPartition(
                        each_disk,
                        checked_logical_disk
                    )
                    self['Partitions'].append(dummy_partition)
                    each_disk.add_partition(dummy_partition)
                    checked_logical_disk.add_partition(dummy_partition)

    def _add_logical_disk(self, logical_disk: 'LogicalDisk') -> 'LogicalDisk':
        return_logical_disk = None
        for each_logical_disk in self['Logical Disks']:
            if each_logical_disk['Name'] == logical_disk['Name']:
                return_logical_disk = each_logical_disk
                break
        if not return_logical_disk:
            return_logical_disk = logical_disk
            self['Logical Disks'].append(logical_disk)
        return return_logical_disk


class LinuxPhysicalDisk(PhysicalDisk):
    def __init__(
        self,
        system: SystemComponent,
        major_number: int,
        minor_number: int,
        size_in_sectors: int,
        device_name: str
    ) -> None:
        super().__init__(system)
        self['Major'] = major_number
        self['Minor'] = minor_number
        self._set_name_and_path(device_name)
        self._set_size_and_sectors(size_in_sectors)

    def _set_size_and_sectors(
        self,
        sectors: int,
        sector_size: int = 512
    ) -> None:
        """Sets number of sectors, sectors size, and size in bytes."""
        self['Sectors'] = sectors
        self['Bytes per Sector'] = sector_size
        self['Size'] = sectors * sector_size

    def _set_name_and_path(self, name):
        self['Name'] = name
        self['Path'] = f'/dev/{name}'


class LinuxPartition(Partition):
    def __init__(
        self,
        disk: 'PhysicalDisk',
        major_number: int,
        minor_number: int,
        size_in_sectors: int,
        device_name: str
    ) -> None:
        super().__init__(disk)
        self['Major Number'] = major_number
        self['Minor Number'] = minor_number
        self._set_device_id_and_path(device_name)
        self._set_blocks_and_size(size_in_sectors)

    def _set_blocks_and_size(
        self,
        sectors: int,
        sector_size: int = 512
    ) -> None:
        self['Number of Blocks'] = sectors
        self['Size'] = sectors * sector_size
        self['Blocksize']

    def _set_device_id_and_path(self, name: str) -> None:
        self['Device I.D.'] = name
        self['Path'] = f'/dev/{name}'


class LinuxLogicalDisk(LogicalDisk):
    def __init__(
        self,
        system: object,
        path: str,
        file_system: str,
        size: int,
        free_space: int
    ) -> None:
        super().__init__(system)
        self._set_path_device_id_and_name(path)
        self['Filesystem'] = file_system
        self['Size'] = size
        self['Free Space'] = free_space

    def _set_path_device_id_and_name(self, path):
        self['Path'] = path
        self['Device I.D.'] = path
        self['Name'] = path