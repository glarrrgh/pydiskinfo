import sys

from system import System
from linux_system import LinuxSystem
from exceptions import PyDiskInfoParseError
if sys.platform == 'win32':
    from windows_system import WindowsSystem


def create_system(name: str = '') -> System:
    if sys.platform == 'win32':
        return WindowsSystem(name=name)
    elif sys.platform == 'linux':
        return LinuxSystem(name=name)
    else:
        raise PyDiskInfoParseError(
            f'Incompatible system type "{sys.platform}"'
        )
