# commandline tests
import platform
from unittest import TestCase
from unittest.mock import patch
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from src.pydiskinfo import pdi_util
import subprocess
import os.path
import re
from tests.fake_wmi import FakeWMIcursor

class CommandlineTests(TestCase):
    def setUp(self) -> None:
        self.commandline = None
        if platform.system() == 'Windows':
            self.commandline = ['py', '-3', '-m', 'src.pydiskinfo']
        elif platform.system() == 'Linux':
            self.commandline = ['python3', '-m', 'src.pydiskinfo']
    
    def get_output(self, arguments: list = None) -> str:
        if not arguments:
            arguments = []
        with patch(
            'wmi.WMI',
            FakeWMIcursor
        ), redirect_stdout(
            StringIO()
        ) as output_stream, redirect_stderr(
            StringIO()
        ) as stderr_stream, patch(
            'sys.argv',
            ['pydiskinfo'] + arguments
        ):
            pdi_util.main()
        if stderr_stream.getvalue():
            raise AssertionError(
                f'Failed running main with "{" ".join(arguments)}"'
                ' option:\n' +
                stderr_stream.getvalue()
            )
        return output_stream.getvalue()
        
    def test_default_commandline_usage(self) -> None:
        """
        Testing the commandline tool with default options from a users
        perspective.
        """
        
        """
        Charlotte run the command pdiutil from the command line interface.
        """
        output = self.get_output()
        
        """
        Charlotte can see some output describing the disks connected to her pc
        """
        out_re = re.compile(
            r'System -- Name: [\S ]*, Type: [\S ]*, Version: [\S ]*\n.*'
            r'Physical Disk -- Disk Number: [\S ]*, Path: [\S ]*'
            r', Media: [\S ]*, Serial: [\S ]*, Size: -?[\d\.]+[GMKTP]?B?\n.*'
            r'Partition -- Device I.D.: [\S ]*, Type: [\S ]*'
            r', Size: -?[\d\.]+[GMKTP]?B?, Offset: -?\d+\n.*'
            r'Logical Disk -- Path: [\S ]*, Label: [\S ]*, Filesystem: [\S ]*'
            r', Free Space: -?[\d\.]+[GMKTP]?B?\n.*',
            re.DOTALL
        )
        self.assertRegex(
            output,
            out_re
        )
        
        """
        Charlotte tries the regular help option -h, and sees some help text
        describing options
        """
        output = self.get_output(['-h'])
        out_re = re.compile(            
            r'.+Start listing from a logical disk viewpoint\. Remember.+'
            r'according to the string, except for the partition list\.\n'
            r'Default: -dp Piptns\n.+'
            r'\nLogical disk properties:\n.+',
            re.DOTALL
        )
        self.assertRegex(
            output,
            out_re
        )
        
        """
        Charlotte tries some output filtering options
        """
        output = self.get_output(['-pp', 'LrSt', '-dp', 'PShta', '-lp', 'VMn'])
        out_re = re.compile(            
            r'System -- Name: [\S ]*, Type: [\S ]*, Version: [\S ]*\n.*'
            r'Physical Disk -- Size: \d+, Heads: \d+, Media: [\S ]*'
            r', Status: [\S ]*\n.*'
            r'Partition -- Primary: (True|False), Size: \d+, Type: [\S ]*\n.*'
            r'Logical Disk -- Label: [\S ]*, Mounted: [\S ]*,'
            r' Serial: [\S ]*\n.*',
            re.DOTALL
        )
        self.assertRegex(
            output,
            out_re
        )

        """
        Charlotte tries the -l option and can see that the output is reversed
        """
        with patch(
            'wmi.WMI',
            FakeWMIcursor
        ), redirect_stdout(
            StringIO()
        ) as output_stream, redirect_stderr(
            StringIO()
        ) as stderr_stream, patch(
            'sys.argv',
            ['pydiskinfo', '-l']
        ):
            pdi_util.main()
        if stderr_stream.getvalue():
            raise AssertionError(
                'Failed running main with -l option:\n' +
                stderr_stream.getvalue()
            )
        output = output_stream.getvalue()
        out_re = re.compile(
            r'System -- [\S ]+?\n'
            r'  Logical Disk -- [\S ]+?\n'
            r'    Partition -- [\S ]+?\n'
            r'      Physical Disk -- [\S ]+?\n'
        )
        self.assertRegex(output, out_re)

        """
        Charlotte tries the -p option and can see that the output skips the
        physical disks
        """
        with patch(
            'wmi.WMI',
            FakeWMIcursor
        ), redirect_stdout(
            StringIO()
        ) as output_stream, redirect_stderr(
            StringIO()
        ) as stderr_stream, patch(
            'sys.argv',
            ['pydiskinfo', '-p']
        ):
            pdi_util.main()
        if stderr_stream.getvalue():
            raise AssertionError(
                'Failed running main with -p option:\n' +
                stderr_stream.getvalue()
            )
        output = output_stream.getvalue()
        out_re = re.compile(
            r'System -- [\S ]+?\n'
            r'  Partition -- [\S ]+?\n'
            r'    Logical Disk -- [\S ]+?\n'
        )
        self.assertRegex(output, out_re)

        """
        Charlotte tries the -l and -p option at the same time, and can see
        that the output start with partition and is reveresed
        """
        with patch(
            'wmi.WMI',
            FakeWMIcursor
        ), redirect_stdout(
            StringIO()
        ) as output_stream, redirect_stderr(
            StringIO()
        ) as stderr_stream, patch(
            'sys.argv',
            ['pydiskinfo', '-p', '-l']
        ):
            pdi_util.main()
        if stderr_stream.getvalue():
            raise AssertionError(
                'Failed running main with -p option:\n' +
                stderr_stream.getvalue()
            )
        output = output_stream.getvalue()
        out_re = re.compile(
            r'System -- [\S ]+?\n'
            r'  Partition -- [\S ]+?\n'
            r'    Physical Disk -- [\S ]+?\n'
        )
        self.assertRegex(output, out_re)
