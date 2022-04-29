"""
Making regular classes available through the package
"""
from . exceptions import PyDiskInfoParseError
from . logical_disk import LogicalDisk
from . partition import Partition
from . physical_disk import PhysicalDisk
from . system import System

__all__ = [
    'PyDiskInfoParseError',
    'LogicalDisk',
    'Partition',
    'PhysicalDisk',
    'System'
]
