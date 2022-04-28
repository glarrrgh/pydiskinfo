# commandline tests
import platform
import unittest
import subprocess


class CommandlineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.commandline = None
        if platform.system() == 'Windows':
            self.commandline = ['py', '-3', '.']
        elif platform.system() == 'Linux':
            self.commandline = ['python3', '.']

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
            raise AssertionError(str(callerr))
        except subprocess.SubprocessError as suberr:
            raise AssertionError(str(suberr))
        """
        Charlot can se some output
        """
        self.assertGreater(len(output), 0)
