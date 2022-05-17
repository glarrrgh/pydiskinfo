from unittest import TestCase
import subprocess
import os
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO
from unittest.mock import patch
from src.pydiskinfo.argument_parsing import get_arguments
from src.pydiskinfo import pdi_util
from tests.fake_wmi import get_windows_system, get_windows_output


class PackageTests(TestCase):
    def test_package_execution(self) -> None:

        self.assertTrue(
            os.path.isfile(
                os.path.normpath('src/pydiskinfo/__main__.py')
                )
            )


class OutputTests(TestCase):
    """Testing the command line input (arguments) and output"""
    def test_default_output_on_windows(self) -> None:
        self.assertRegex(
            get_windows_output(),
            'System -- Name: Some system, Type: Windows, Version: test 10\n'
            r'  Physical Disk -- Disk Number: \d+, Path: Some device id, '
            'Media: Some media type, Serial: Some serial, Size: 256.05GB\n'
            r'    Partition -- Device I.D.: Partition\d+ Disk\d+, '
            'Type: Some type, Size: 104.86MB, Offset: 1048576\n'
            '      Logical Disk -- Label: Some label,'
            ' Filesystem: Some filesystem, Free Space: 800.00MB\n'
        )

    def test_help_output_on_windows(self) -> None:
        self.assertRegex(
            get_windows_output(['-h']),
            r'The default behaviour is to list all devices from the system'
            r' down through\nphysical disk and partitions, to logical disks\.'
            r' The partitions are only\n"physical" partitions'
        )

    def test_indentations(self) -> None:
        """Test that indentations are correctly expanding with items"""
        wmi_setup = [
            'physical disk',
            [
                'partition',
                [
                    'logical disk',
                    'logical disk'
                ],
                'partition',
                'partition',
                [
                    'logical disk'
                ]
            ],
            'physical disk',
            'physical disk',
            [
                'partition',
                [
                    'logical disk'
                ],
                'partition',
                [
                    'logical disk'
                ]
            ]
        ]
        self.assertRegex(
            get_windows_output(['-dp', 'Pi', '-pp', 'Ldi'], wmi_setup),
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
            get_windows_output(['-dp', 'Pi', '-pp', 'LDdi', '-l'], wmi_setup),
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
            get_windows_output(['-dp', 'Pi', '-pp', 'LDdi', '-p'], wmi_setup),
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
            get_windows_output(['-dp', 'i', '-pp', 'di', '-p'], wmi_setup),
            r'^System -- [\S ]+?\n'
            r'  Partition -- [\S ]+?\n'
            r'  Partition -- [\S ]+?\n'
            r'  Partition -- [\S ]+?\n'
            r'  Partition -- [\S ]+?\n'
            r'  Partition -- [\S ]+?\n$'
        )
        self.assertRegex(
            get_windows_output(
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
            get_windows_output(['-dp', 'i'], wmi_setup),
            r'^System -- [\S ]+?\n'
            r'  Physical Disk -- [\S ]+?\n'
            r'  Physical Disk -- [\S ]+?\n'
            r'  Physical Disk -- [\S ]+?\n$'
        )
        self.assertRegex(
            get_windows_output(['-lp', 'V', '-l'], wmi_setup),
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
        system_string = pdi_util.stringify(system)
        self.assertEqual(
            system_string,
            'System -- '
            'Name: Some system, '
            'Type: Windows, '
            'Version: test 10'
        )

    @patch('sys.argv', [
        'pydiskinfo',
        '-dp',
        'PXSsidptnmcbhCfIMa'
    ])
    def test_str_physical_disk(self) -> None:
        self.maxDiff = None
        physical_disk_string = pdi_util.stringify(
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
        partition_string = pdi_util.stringify(
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
            r'Device I.D.: Partition\d+ Disk\d+, '
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
        logical_disk_string = pdi_util.stringify(
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


class LineAssemblerTests(TestCase):
    def test_str_output(self) -> None:
        with patch('sys.argv', ['pydiskinfo']):
            arguments = get_arguments()
        self.assertRegex(
            str(pdi_util.LineAssembler(
                arguments,
                get_windows_system()
            )),
            r'^System -- [\S ]+\n'
            r'  Physical Disk -- [\S ]+\n'
            r'    Partition -- [\S ]+\n'
            r'      Logical Disk -- [\S ]+$'
        )
