# commandline tests
import platform
import unittest
import subprocess
import os.path
import re


class CommandlineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.commandline = None
        if platform.system() == 'Windows':
            self.commandline = ['py', '-3', '-m', 'src.pydiskinfo']
        elif platform.system() == 'Linux':
            self.commandline = ['python3', '-m', 'src.pydiskinfo']
    
    def get_output(self, arguments: list = None) -> str:
        if not arguments:
            arguments = []
        try:
            output = subprocess.run(
                self.commandline + arguments,
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
        return output

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
            r', Media: [\S ]*, Serial: [\S ]*, Size: [\d\.]+[GMKTP]?B?\n.*'
            r'Partition -- Device I.D.: [\S ]*, Type: [\S ]*'
            r', Size: [\d\.]+[GMKTP]?B?, Offset: \d+\n.*'
            r'Logical Disk -- Path: [\S ]*, Label: [\S ]*, Filesystem: [\S ]*'
            r', Free Space: [\d\.]+[GMKTP]?B?\n.*',
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
