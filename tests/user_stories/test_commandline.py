# commandline tests
import platform
import unittest
import subprocess
import os.path


class CommandlineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.commandline = None
        if platform.system() == 'Windows':
            self.commandline = ['py', '-3', '-m', 'src.pydiskinfo']
        elif platform.system() == 'Linux':
            self.commandline = ['python3', os.path.normpath('src/pydiskinfo')]

    def test_default_commandline_usage(self) -> None:
        """
        Testing the commandline tool with default options from a users
        perspective.
        """
        """
        Charlot run the command pdiutil from the command line interface.
        """
        try:
            output = subprocess.run(
                self.commandline,
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
        """
        Charlot can se some output describing the disks connected to her pc
        """
        self.assertRegexpMatches(output,
            '^System -- .*?'
            '\nPhysical disk -- .*?'
            '\nPartition -- .*?'
            '\nLogical disk -- .*?'
            )
