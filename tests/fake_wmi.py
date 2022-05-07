from unittest.mock import patch
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from io import StringIO
from src.pydiskinfo.system import System, create_system
from src.pydiskinfo.pdi_util import main


class FakeWMILogicalDisk:
    def __init__(self, number: int) -> None:
        self.Description = 'Some description'
        self.DeviceID = f'device{number}'
        self.DriveType = '0'
        self.FileSystem = 'Some filesystem'
        self.FreeSpace = '800000000'
        self.MaximumComponentLength = '255'
        self.Size = '1000000000'
        self.VolumeName = 'Some label'
        self.VolumeSerialNumber = 'Some serial'


class FakeWMIPartition:
    def __init__(self, number: int, disk_number: int) -> None:
        self._logical_disks = []
        self.BlockSize = '512'
        self.Bootable = True
        self.BootPartition = True
        self.Description = 'Some description'
        self.DeviceID = f'Partition{number} Disk{disk_number}'
        self.DiskIndex = str(disk_number)
        self.Index = str(number)
        self.NumberOfBlocks = '204800'
        self.PrimaryPartition = True
        self.Size = '104857600'
        self.StartingOffset = '1048576'
        self.Type = 'Some type'

    def associators(self, association: str) -> list:
        return self._logical_disks

    def _add_logical_disk(self, logical_disk: FakeWMILogicalDisk) -> None:
        self._logical_disks.append(logical_disk)


class FakeWMIPhysicalDisk:
    def __init__(self, number: int) -> None:
        self._partitions = []
        self.Size = '256052966400'
        self.Index = str(number)
        self.DeviceID = 'Some device id'
        self.MediaType = 'Some media type'
        self.SerialNumber = 'Some serial'
        self.Model = 'Some model'
        self.TotalSectors = '500103450'
        self.TotalHeads = '255'
        self.TotalCylinders = '31130'
        self.BytesPerSector = '512'
        self.FirmWare = 'Some firmware'
        self.InterfaceType = 'Some interface'
        self.MediaLoaded = True
        self.Status = 'OK'

    def associators(self, association: str) -> list:
        return self._partitions

    def _add_partition(self, partition: FakeWMIPartition) -> None:
        """Add another partition to the physical disk"""
        self._partitions.append(partition)


class FakeWMIcursor:
    def __init__(self, configuration: list = None) -> None:
        self._physical_disk_number = 0
        self._logical_disk_number = 0
        self._physical_disks = self._parse_configuration(configuration)

    def _parse_configuration(self, configuration: list) -> list:
        if configuration is None:
            configuration = [
                'physicaldisk',
                [
                    'partition',
                    ['logicaldisk']
                ]
            ]
        physical_disks = []
        physical_disk = None
        for each_physical_disk in configuration:
            if isinstance(each_physical_disk, list):
                partition_number = 0
                partition = None
                for each_partition in each_physical_disk:
                    if isinstance(each_partition, list):
                        for each_logical_disk in each_partition:
                            partition._add_logical_disk(
                                FakeWMILogicalDisk(
                                    number=self._logical_disk_number
                                )
                            )
                            self._logical_disk_number += 1
                    else:
                        partition = FakeWMIPartition(
                            number=partition_number,
                            disk_number=self._physical_disk_number
                        )
                        partition_number += 1
                        physical_disk._add_partition(partition)
            else:
                physical_disk = FakeWMIPhysicalDisk(
                    number=self._physical_disk_number
                )
                self._physical_disk_number += 1
                physical_disks.append(physical_disk)
        return physical_disks

    def Win32_DiskDrive(self) -> list:
        return self._physical_disks


def get_windows_system(configuration: list = None, name: str = '') -> System:
    """return a fake System object for test purposes"""
    with patch_windows(configuration=configuration, name=name):
        system = create_system()
    return system


@contextmanager
def patch_windows(
    configuration: list = None,
    name: str = ''
):
    def create_fake_cursor() -> FakeWMIcursor:
        return FakeWMIcursor(configuration)

    with patch(
        target='wmi.WMI',
        new=create_fake_cursor
    ), patch(
        target='sys.platform',
        new='win32'
    ), patch(
        target='socket.gethostname'
    ) as fake_gethostname, patch(
        target='src.pydiskinfo.system.platform'
    ) as fake_platform:
        fake_platform.win32_edition.return_value = 'test'
        fake_platform.win32_ver.return_value = ['notused', '10']
        fake_platform.system.return_value = 'Some type'
        if name:
            fake_gethostname.return_value = name
        else:
            fake_gethostname.return_value = 'Some system'
        yield


def get_windows_output(
    arguments: list = None,
    configuration: list = None,
    name: str = ''
) -> str:
    """Return output from pydiskinfo given certain arguments"""
    if arguments is None:
        arguments = []
    with patch_windows(
        configuration=configuration,
        name=name
    ), patch(
        target='sys.argv',
        new=['pydiskinfo'] + arguments
    ), redirect_stdout(
        new_target=StringIO()
    ) as output_stream, redirect_stderr(
        new_target=StringIO()
    ) as error_stream:
        main()
    if error_stream.getvalue():
        raise AssertionError(
            'pydiskinfo.pdi_util.main returned some errors\n'
            f'stderr:\n{error_stream.getvalue()}\n'
            f'stdout:\n{output_stream.getvalue()}\n'
        )
    return output_stream.getvalue()
