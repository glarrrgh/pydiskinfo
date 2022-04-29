from typing import Tuple
from unittest import TestCase, mock
import subprocess
import platform
import os
from unittest.mock import patch, Mock
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


def mocked_Win32_DiskDrive(self) -> Mock:
    return_mock = Mock()
    return_mock.size = '1610612736'
    return return_mock


class OutputTests(TestCase):
    @patch('wmi.WMI')
    @patch('sys.platform', 'win32')
    def test_default_output_on_windows(self) -> None:
        # plaftorm_mock.return_value

        try:
            output = subprocess.run(
                ('py', '-3', '-m', 'src.pydiskinfo'),
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
        self.assertEqual(output,
'''System -- Name: Some system, Type: Some type, Version: 10
  Physical disk -- Disk number: 0, Path: Some Path, Media type: Some media type, Serial: Some serial, Size: 1.5GB
    Partition -- Devide I.D.: Some device id, Type: Some type, Size: 1GB, Offset: 1024
      Logical disk -- Path: Some path, Volume name: Some label, File system: Some filesystem, Free space: 800MB\n''')

    @patch('sys.argv', [
        'pydiskinfo',
    ])
    def test_default_get_arguments(self) -> None:
        arguments = get_arguments()
        self.assertEqual(arguments, {
            'dp': 'Pipts',
            'pp': 'LDdtse',
            'lp': 'PpVtfF',
            'l': False,
            'n': None,
            'p': False})
