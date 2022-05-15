import sys

from . import System
# from . system import LinuxSystem
from . import PyDiskInfoParseError
if sys.platform == 'win32':
    from . windows_system import WindowsSystem


def create_system(name: str = '') -> System:
    if sys.platform == 'win32':
        return WindowsSystem(name=name)
    # elif sys.platform == 'linux':
    #     return LinuxSystem(name=name)
    else:
        raise PyDiskInfoParseError(
            f'Incompatible system type "{sys.platform}"'
        )
