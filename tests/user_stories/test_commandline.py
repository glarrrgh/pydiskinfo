# commandline tests
from unittest import TestCase
from unittest.mock import patch
import re
from tests.fake_wmi import get_windows_output


class CommandlineTests(TestCase):
    def test_default_commandline_usage(self) -> None:
        """
        Testing the commandline tool with default options from a users
        perspective.
        """

        """
        Charlotte run the command pdiutil from the command line interface.
        """
        output = get_windows_output()
        """
        Charlotte can see some output describing the disks connected to her pc
        """
        out_re = re.compile(
            r'^System -- Name: [\S ]*, Type: [\S ]*, Version: [\S ]*\n.*'
            r'Physical Disk -- Disk Number: [\S ]*, Path: [\S ]*'
            r', Media: [\S ]*, Serial: [\S ]*, Size: -?[\d\.]+[GMKTP]?B?\n.*'
            r'Partition -- Device I.D.: [\S ]*, Type: [\S ]*'
            r', Size: -?[\d\.]+[GMKTP]?B?, Offset: -?\d+\n.*'
            r'Logical Disk -- Label: [\S ]*, Filesystem: [\S ]*'
            r', Free Space: -?[\d\.]+[GMKTP]?B?\n',
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
        output = get_windows_output(['-h'])
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
        output = get_windows_output(
            ['-pp', 'LrSt', '-dp', 'PShta', '-lp', 'VMn']
        )
        out_re = re.compile(
            r'^System -- Name: [\S ]*, Type: [\S ]*, Version: [\S ]*\n.*'
            r'Physical Disk -- Size: \d+, Heads: \d+, Media: [\S ]*'
            r', Status: [\S ]*\n.*'
            r'Partition -- Primary: (True|False), Size: \d+, Type: [\S ]*\n.*'
            r'Logical Disk -- Label: [\S ]*, Mounted: [\S ]*,'
            r' Serial: [\S ]*\n$',
            re.DOTALL
        )
        self.assertRegex(
            output,
            out_re
        )

        """
        Charlotte tries the -l option and can see that the output is reversed
        """
        output = get_windows_output(['-l'])
        out_re = re.compile(
            r'^System -- [\S ]+?\n'
            r'  Logical Disk -- [\S ]+?\n'
            r'    Partition -- [\S ]+?\n'
            r'      Physical Disk -- [\S ]+?\n$'
        )
        self.assertRegex(output, out_re)

        """
        Charlotte tries the -p option and can see that the output skips the
        physical disks
        """
        output = get_windows_output(['-p'])
        out_re = re.compile(
            r'^System -- [\S ]+?\n'
            r'  Partition -- [\S ]+?\n'
            r'    Logical Disk -- [\S ]+?\n$'
        )
        self.assertRegex(output, out_re)

        """
        Charlotte tries the -l and -p option at the same time, and can see
        that the output starts with partition and is reveresed
        """
        output = get_windows_output(['-p', '-l'])
        out_re = re.compile(
            r'^System -- [\S ]+?\n'
            r'  Partition -- [\S ]+?\n'
            r'    Physical Disk -- [\S ]+?\n$'
        )
        self.assertRegex(output, out_re)

        """
        Charlotte tries the -dp option without P, and can see that only the
        physical disks are displayd
        """
        output = get_windows_output(['-dp', 'ms'])
        self.assertRegex(
            output,
            r'^System -- [\S ]+?\n'
            r'  Physical Disk -- [\S ]+?\n$'
        )

        """
        Charlotte tries the -pp option without L, and can see that only the
        physical disks and their partitions are displayd
        """
        output = get_windows_output(['-pp', 'Ns'])
        self.assertRegex(
            output,
            r'^System -- [\S ]+?\n'
            r'  Physical Disk -- [\S ]+?\n'
            r'    Partition -- [\S ]+?\n$'
        )

        """
        Charlotte tries the -p and -pp option without L, and can see that
        only the partitions are displayd
        """
        output = get_windows_output(['-pp', 'Ns', '-p'])
        self.assertRegex(
            output,
            r'^System -- [\S ]+?\n'
            r'  Partition -- [\S ]+?\n$'
        )

        """
        Charlotte types the wrong option -X and gets a message that the
        option is unrecognized
        """
        self.assertRaisesRegex(AssertionError, r'.+\npydiskinfo: error: unrecognized arguments: -X\n', get_windows_output, ['-X'])

        """
        Charlotte tries the -l and -pp option without D, and can see that
        only the logical disks and their partitions are displayd
        """
        output = get_windows_output(['-pp', 'Ns', '-l'])
        self.assertRegex(
            output,
            r'^System -- [\S ]+?\n'
            r'  Logical Disk -- [\S ]+?\n'
            r'    Partition -- [\S ]+?\n$'
        )

        """
        Charlotte tries the -l, -p and -pp option without D, and can see that
        only the partitions are displayd
        """
        output = get_windows_output(['-pp', 'Ns', '-l', '-p'])
        self.assertRegex(
            output,
            r'^System -- [\S ]+?\n'
            r'  Partition -- [\S ]+?\n$'
        )
