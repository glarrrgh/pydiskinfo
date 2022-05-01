from unittest import TestCase
import subprocess
import platform
import os
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO
from unittest.mock import patch
from src.pydiskinfo.argument_parsing import get_arguments
from src.pydiskinfo import pdi_util
from src.pydiskinfo.argument_parsing import get_arguments


class PackageTests(TestCase):
    def test_package_execution(self) -> None:

        self.assertTrue(
            os.path.isfile(
                os.path.normpath('src/pydiskinfo/__main__.py')
                )
            )


"""
windows mock methods
"""


def get_system_dict(name: str = 'ignored') -> dict:
    class DictClassWrapper(dict):
        def __init__(self, input_dict: dict) -> None:
            super().__init__(input_dict)
    system = DictClassWrapper({
        'Name': 'Some system',
        'Type': 'Some type',
        'Version': '10',
        'Physical Disks': None,
        'Partitions': None,
        'Logical Disks': None
    })
    physical_disk = DictClassWrapper({
        'System': system,
        'Partitions': None,
        'Size': 256052966400,
        'Disk Number': 0,
        'Path': 'Some path',
        'Device I.D.': 'Some device id',
        'Media': 'Some media type',
        'Serial': 'Some serial',
        'Model': 'Some model',
        'Sectors': 500103450,
        'Heads': 255,
        'Cylinders': 31130,
        'Bytes per Sector': 512,
        'Firmware': 'Some firmware',
        'Interface': 'Some interface',
        'Media Loaded': True,
        'Status': 'OK'
    })
    partition = DictClassWrapper({
        'Physical Disk': physical_disk,
        'Logical Disks': None,
        'Blocksize': 512,
        'Bootable': True,
        'Active': True,
        'Description': 'Some description',
        'Path': 'Some path',
        'Device I.D.': 'Some device id',
        'Disk Number': physical_disk['Disk Number'],
        'Partition Number': 0,
        'Blocks': 204800,
        'Primary': True,
        'Size': 104857600,
        'Offset': 1048576,
        'Type': 'Some type'
    })
    logical_disk = DictClassWrapper({
        'System': system,
        'Partitions': [partition],
        'Description': 'Some description',
        'Device I.D.': 'Some device id',
        'Type': 'Some type',
        'Filesystem': 'Some filesystem',
        'Free Space': 800000000,
        'Max Component Length': 255,
        'Name': 'Some name',
        'Path': 'Some path',
        'Mounted': 'Somewhere',
        'Size': 1000000000,
        'Label': 'Some label',
        'Serial': 'Some serial'
    })
    system['Physical Disks'] = [physical_disk]
    system['Partitions'] = [partition]
    system['Logical Disks'] = [logical_disk]
    physical_disk['Partitions'] = [partition]
    partition['Logical Disks'] = [logical_disk]
    partition.isdummy = False
    return system


class OutputTests(TestCase):
    def test_default_output_on_windows(self) -> None:
        self.maxDiff = None
        with patch(
                'sys.argv',
                ['pydiskinfo']
            ), patch(
                'src.pydiskinfo.pdi_util.System',
                get_system_dict
            ), redirect_stdout(
                StringIO()
            ) as output_stream, redirect_stderr(
                StringIO()
            ) as stderr_stream:
            pdi_util.main()
        self.assertEqual(stderr_stream.getvalue(), '')
        self.assertEqual(output_stream.getvalue(),
'''System -- Name: Some system, Type: Some type, Version: 10
  Physical Disk -- Disk Number: 0, Path: Some path, Media: Some media type, Serial: Some serial, Size: 256.05GB
    Partition -- Device I.D.: Some device id, Type: Some type, Size: 104.86MB, Offset: 1048576
      Logical Disk -- Path: Some path, Label: Some label, Filesystem: Some filesystem, Free Space: 800.00MB\n'''
        )

    def test_help_output_on_windows(self) -> None:
        try:
            output = subprocess.run(
                ('py', '-3', '-m', 'src.pydiskinfo', '-h'),
                capture_output=True,
                text=True,
                check=True
                ).stdout
        except ValueError as valerr:
            raise AssertionError(str(valerr))
        except subprocess.CalledProcessError as callerr:
            raise AssertionError(f'{str(callerr)}\n########\n{callerr.stderr}')
        except subprocess.SubprocessError as suberr:
            raise AssertionError(str(suberr))
        self.assertRegex(output,
r'''.*The default behaviour is to list all devices from the system down through
physical disk and partitions, to logical disks\. The partitions are only
"physical" partitions.*''')


class StringFunctions(TestCase):
    def test_str_system(self) -> None:
        system = get_system_dict()
        system_string = pdi_util.str_system(system)
        self.assertEqual(
            system_string,
            'System -- '
            'Name: Some system, '
            'Type: Some type, '
            'Version: 10'
        )

    @patch('sys.argv', [
        'pydiskinfo',
        '-dp',
        'PXSsidptnmcbhCfIMa'
    ])
    def test_str_physical_disk(self) -> None:
        self.maxDiff = None
        physical_disk_string = pdi_util.str_physical_disk(
            get_system_dict()['Physical Disks'][0],
            get_arguments()
        )
        self.assertEqual(
            physical_disk_string,
            'Physical Disk -- '
            'Size: 256.05GB, '
            'Disk Number: 0, '
            'Device I.D.: Some device id, '
            'Path: Some path, '
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
            get_system_dict()['Physical Disks'][0]['Partitions'][0],
            get_arguments()
        )
        self.assertEqual(
            partition_string,
            'Partition -- '
            'Blocksize: 512, '
            'Bootable: True, '
            'Active: True, '
            'Description: Some description, '
            'Path: Some path, '
            'Device I.D.: Some device id, '
            'Disk Number: 0, '
            'Partition Number: 0, '
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
            get_system_dict()
            ['Physical Disks'][0]
            ['Partitions'][0]
            ['Logical Disks'][0],
            get_arguments()
        )
        self.assertEqual(
            logical_disk_string,
            'Logical Disk -- '
            'Description: Some description, '
            'Device I.D.: Some device id, '
            'Type: Some type, '
            'Filesystem: Some filesystem, '
            'Free Space: 800.00MB, '
            'Max Component Length: 255, '
            'Name: Some name, '
            'Path: Some path, '
            'Mounted: Somewhere, '
            'Size: 1.00GB, '
            'Label: Some label, '
            'Serial: Some serial'
        )
