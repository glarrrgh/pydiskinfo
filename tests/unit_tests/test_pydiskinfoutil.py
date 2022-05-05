from unittest import TestCase
import subprocess
import os
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO
from unittest.mock import patch
from src.pydiskinfo.argument_parsing import get_arguments
from src.pydiskinfo import pdi_util
from tests.fake_wmi import (
    FakeWMIcursor,
    FakeWMIPhysicalDisk,
    FakeWMIPartition,
    FakeWMILogicalDisk,
    get_windows_system
)


class PackageTests(TestCase):
    def test_package_execution(self) -> None:

        self.assertTrue(
            os.path.isfile(
                os.path.normpath('src/pydiskinfo/__main__.py')
                )
            )


# def get_system_dict(name: str = 'ignored') -> dict:
#     """Returns a fake System object"""
#     class DictClassWrapper(dict):
#         """Allows for adding properties dynamically"""
#         def __init__(self, input_dict: dict) -> None:
#             super().__init__(input_dict)
#             self._physical_disks = []

#         def get_physical_disks(self) -> 'DictClassWrapper':
#             return tuple(self._physical_disks)

#     system = DictClassWrapper({
#         'Name': 'Some system',
#         'Type': 'Some type',
#         'Version': '10',
#         'Physical Disks': None,
#         'Partitions': None,
#         'Logical Disks': None
#     })
#     physical_disk = DictClassWrapper({
#         'System': system,
#         'Partitions': None,
#         'Size': 256052966400,
#         'Disk Number': 0,
#         'Path': 'Some path',
#         'Device I.D.': 'Some device id',
#         'Media': 'Some media type',
#         'Serial': 'Some serial',
#         'Model': 'Some model',
#         'Sectors': 500103450,
#         'Heads': 255,
#         'Cylinders': 31130,
#         'Bytes per Sector': 512,
#         'Firmware': 'Some firmware',
#         'Interface': 'Some interface',
#         'Media Loaded': True,
#         'Status': 'OK'
#     })
#     partition = DictClassWrapper({
#         'Physical Disk': physical_disk,
#         'Logical Disks': None,
#         'Blocksize': 512,
#         'Bootable': True,
#         'Active': True,
#         'Description': 'Some description',
#         'Path': 'Some path',
#         'Device I.D.': 'Some device id',
#         'Disk Number': physical_disk['Disk Number'],
#         'Partition Number': 0,
#         'Blocks': 204800,
#         'Primary': True,
#         'Size': 104857600,
#         'Offset': 1048576,
#         'Type': 'Some type'
#     })
#     logical_disk = DictClassWrapper({
#         'System': system,
#         'Partitions': [partition],
#         'Description': 'Some description',
#         'Device I.D.': 'Some device id',
#         'Type': 'Some type',
#         'Filesystem': 'Some filesystem',
#         'Free Space': 800000000,
#         'Max Component Length': 255,
#         'Name': 'Some name',
#         'Path': 'Some path',
#         'Mounted': 'Somewhere',
#         'Size': 1000000000,
#         'Label': 'Some label',
#         'Serial': 'Some serial'
#     })
#     system._physical_disks = [physical_disk]
#     system._partitions = [partition]
#     system._logical_disks = [logical_disk]
#     physical_disk._partitions = [partition]
#     partition._logical_disks = [logical_disk]
#     partition.isdummy = False
#     return system


class OutputTests(TestCase):
    """Testing the command line input (arguments) and output"""
    def get_output(
        self, arguments: list = None,
        wmi_setup: list = None
        ) -> str:
        if arguments is None:
            arguments = []
        with patch(
            'sys.platform',
            'win32'
        ), patch(
            'wmi.WMI',
            new=lambda: FakeWMIcursor(wmi_setup)
        ), redirect_stdout(
            StringIO()
        ) as output_stream, redirect_stderr(
            StringIO()
        ) as stderr_stream, patch(
            'sys.argv',
            ['pydiskinfo'] + arguments
        ), patch(
            target='socket.gethostname'
        ) as fake_gethostname, patch(
            target='src.pydiskinfo.system.platform'
        ) as fake_platform:
            fake_gethostname.return_value = 'Some system'
            fake_platform.win32_edition.return_value = 'test'
            fake_platform.win32_ver.return_value = ['notused', '10']
            fake_platform.system.return_value = 'Some type'
            pdi_util.main()
        if stderr_stream.getvalue():
            raise AssertionError(
                'pdi_util.main() wrote to stderr:\n'
                f'{stderr_stream.getvalue()}'
            )
        return output_stream.getvalue()

    def test_default_output_on_windows(self) -> None:
        self.assertRegex(
            self.get_output(),
            'System -- Name: Some system, Type: Some type, Version: test 10\n'
            r'  Physical Disk -- Disk Number: \d+, Path: Some device id, '
            'Media: Some media type, Serial: Some serial, Size: 256.05GB\n'
            r'    Partition -- Device I.D.: Partition \d+ Disk \d+, '
            'Type: Some type, Size: 104.86MB, Offset: 1048576\n'
            '      Logical Disk -- Path: , Label: Some label,'
            ' Filesystem: Some filesystem, Free Space: 800.00MB\n'
        )

    def test_help_output_on_windows(self) -> None:
        self.assertRegex(
            self.get_output(['-h']),
            r'The default behaviour is to list all devices from the system'
            r' down through\nphysical disk and partitions, to logical disks\.'
            r' The partitions are only\n"physical" partitions'
        )

    def test_indentations(self) -> None:
        """Test that indentations are correctly expanding with items"""
        wmi_setup = [
            FakeWMIPhysicalDisk([
                FakeWMIPartition([
                    FakeWMILogicalDisk(),
                    FakeWMILogicalDisk()
                ]),
                FakeWMIPartition([]),
                FakeWMIPartition()
            ]),
            FakeWMIPhysicalDisk([]),
            FakeWMIPhysicalDisk([
                FakeWMIPartition(),
                FakeWMIPartition()
            ])
        ]
        self.assertRegex(
            self.get_output(['-dp', 'Pi', '-pp', 'Ldi'], wmi_setup),
            r'^System -- [\S ]+?\n'
            r'  Physical Disk -- [\S ]+?\n'
            r'    Partition -- [\S ]+?\n'
            r'      Logical Disk -- [\S ]+?\n'
            r'      Logical Disk -- [\S ]+?\n'
            r'    Partition -- [\S ]+?\n'
            r'    Partition -- [\S ]+?\n'
            r'      Logical Disk -- [\S ]+?\n'
            r'  Physical Disk -- [\S ]+?\n'
            r'  Physical Disk -- [\S ]+?\n'
            r'    Partition -- [\S ]+?\n'
            r'      Logical Disk -- [\S ]+?\n'
            r'    Partition -- [\S ]+?\n'
            r'      Logical Disk -- [\S ]+?\n$'
        )
        self.assertRegex(
            self.get_output(['-dp', 'Pi', '-pp', 'LDdi', '-l'], wmi_setup),
            r'^System -- [\S ]+?\n'
            r'  Logical Disk -- [\S ]+?\n'
            r'    Partition -- [\S ]+?\n'
            r'      Physical Disk -- [\S ]+?\n'
            r'  Logical Disk -- [\S ]+?\n'
            r'    Partition -- [\S ]+?\n'
            r'      Physical Disk -- [\S ]+?\n'
            r'  Logical Disk -- [\S ]+?\n'
            r'    Partition -- [\S ]+?\n'
            r'      Physical Disk -- [\S ]+?\n'
            r'  Logical Disk -- [\S ]+?\n'
            r'    Partition -- [\S ]+?\n'
            r'      Physical Disk -- [\S ]+?\n'
            r'  Logical Disk -- [\S ]+?\n'
            r'    Partition -- [\S ]+?\n'
            r'      Physical Disk -- [\S ]+?\n$'
        )
        self.assertRegex(
            self.get_output(['-dp', 'Pi', '-pp', 'LDdi', '-p'], wmi_setup),
            r'^System -- [\S ]+?\n'
            r'  Partition -- [\S ]+?\n'
            r'    Logical Disk -- [\S ]+?\n'
            r'    Logical Disk -- [\S ]+?\n'
            r'  Partition -- [\S ]+?\n'
            r'  Partition -- [\S ]+?\n'
            r'    Logical Disk -- [\S ]+?\n'
            r'  Partition -- [\S ]+?\n'
            r'    Logical Disk -- [\S ]+?\n'
            r'  Partition -- [\S ]+?\n'
            r'    Logical Disk -- [\S ]+?\n$'
        )
        self.assertRegex(
            self.get_output(['-dp', 'i', '-pp', 'di', '-p'], wmi_setup),
            r'^System -- [\S ]+?\n'
            r'  Partition -- [\S ]+?\n'
            r'  Partition -- [\S ]+?\n'
            r'  Partition -- [\S ]+?\n'
            r'  Partition -- [\S ]+?\n'
            r'  Partition -- [\S ]+?\n$'
        )
        self.assertRegex(
            self.get_output(
                ['-dp', 'i', '-pp', 'di', '-lp', 'V', '-p', '-l'],
                wmi_setup
            ),
            r'^System -- [\S ]+?\n'
            r'  Partition -- [\S ]+?\n'
            r'  Partition -- [\S ]+?\n'
            r'  Partition -- [\S ]+?\n'
            r'  Partition -- [\S ]+?\n'
            r'  Partition -- [\S ]+?\n$'
        )
        self.assertRegex(
            self.get_output(['-dp', 'i'], wmi_setup),
            r'^System -- [\S ]+?\n'
            r'  Physical Disk -- [\S ]+?\n'
            r'  Physical Disk -- [\S ]+?\n'
            r'  Physical Disk -- [\S ]+?\n$'
        )
        self.assertRegex(
            self.get_output(['-lp', 'V', '-l'], wmi_setup),
            r'^System -- [\S ]+?\n'
            r'  Logical Disk -- [\S ]+?\n'
            r'  Logical Disk -- [\S ]+?\n'
            r'  Logical Disk -- [\S ]+?\n'
            r'  Logical Disk -- [\S ]+?\n'
            r'  Logical Disk -- [\S ]+?\n$'
        )


class StringFunctions(TestCase):
    def test_str_system(self) -> None:
        system = get_windows_system()
        system_string = pdi_util.str_system(system)
        self.assertEqual(
            system_string,
            'System -- '
            'Name: Some system, '
            'Type: Some type, '
            'Version: test 10'
        )

    @patch('sys.argv', [
        'pydiskinfo',
        '-dp',
        'PXSsidptnmcbhCfIMa'
    ])
    def test_str_physical_disk(self) -> None:
        self.maxDiff = None
        physical_disk_string = pdi_util.str_physical_disk(
            get_windows_system().get_physical_disks()[0],
            get_arguments()
        )
        self.assertRegex(
            physical_disk_string,
            'Physical Disk -- '
            'Size: 256.05GB, '
            r'Disk Number: \d+, '
            'Device I.D.: Some device id, '
            'Path: Some device id, '
            'Media: Some media type, '
            'Serial: Some serial, '
            'Model: Some model, '
            'Sectors: 500103450, '
            'Bytes per Sector: 512, '
            'Heads: 255, '
            'Cylinders: 31130, '
            'Firmware: Some firmware, '
            'Interface: Some interface, '
            'Media Loaded: True, '
            'Status: OK'
        )

    @patch('sys.argv', [
        'pydiskinfo',
        '-pp',
        'LXDbBoxpdiNcrSset',
    ])
    def test_str_partition(self) -> None:
        self.maxDiff = None
        partition_string = pdi_util.str_partition(
            get_windows_system().get_physical_disks()[0].get_partitions()[0],
            get_arguments()
        )
        self.assertRegex(
            partition_string,
            'Partition -- '
            'Blocksize: 512, '
            'Bootable: True, '
            'Active: True, '
            'Description: Some description, '
            'Path: , '
            r'Device I.D.: Partition \d+ Disk \d+, '
            r'Disk Number: \d+, '
            r'Partition Number: \d+, '
            'Blocks: 204800, '
            'Primary: True, '
            'Size: 104.86MB, '
            'Offset: 1048576, '
            'Type: Some type'
        )

    @patch('sys.argv', [
        'pydiskinfo',
        '-lp',
        'PXxdtfFUvpMSsVn',
    ])
    def test_str_logical_disk(self) -> None:
        self.maxDiff = None
        logical_disk_string = pdi_util.str_logical_disk(
            get_windows_system()
            .get_physical_disks()[0]
            .get_partitions()[0]
            .get_logical_disks()[0],
            get_arguments()
        )
        self.assertRegex(
            logical_disk_string,
            'Logical Disk -- '
            'Description: Some description, '
            r'Device I.D.: device\d+, '
            'Type: Unknown, '
            'Filesystem: Some filesystem, '
            'Free Space: 800.00MB, '
            'Max Component Length: 255, '
            r'Name: device\d+, '
            'Path: , '
            r'Mounted: device\d+\\, '
            'Size: 1.00GB, '
            'Label: Some label, '
            'Serial: Some serial'
        )
