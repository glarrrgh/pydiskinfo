from unittest import TestCase
from unittest.mock import patch
from src.pydiskinfo import LogicalDisk
from src.pydiskinfo.partition import Partition
from src.pydiskinfo.physical_disk import PhysicalDisk
from src.pydiskinfo import create_system
from src.pydiskinfo.windows_system import WindowsSystem
from src.pydiskinfo.exceptions import PyDiskInfoParseError
from tests.fake_wmi import get_windows_system


class FactoryTest(TestCase):
    def setUp(self) -> None:
        self.windows_system = get_windows_system()

    """Test object creation"""
    def test_get_system_windows(self) -> None:
        """Test that you get a windowssystem on a windows system"""
        self.assertIsInstance(self.windows_system, WindowsSystem)

    def test_get_system_with_unknown_system(self) -> None:
        with patch(target='sys.platform', new='bogus'):
            self.assertRaises(PyDiskInfoParseError, create_system)


class InformationAccess(TestCase):
    """testing library user's information access"""
    def setUp(self) -> None:
        self.windows_system = get_windows_system()

    def test_get_physical_disks(self) -> None:
        self.assertIsInstance(self.windows_system.get_physical_disks(), tuple)
        [self.assertIsInstance(
            physical_disk,
            PhysicalDisk
        ) for physical_disk in self.windows_system.get_physical_disks()]

    def test_get_partitions(self) -> None:
        self.assertIsInstance(self.windows_system.get_partitions(), tuple)
        [self.assertIsInstance(
            partition,
            Partition
        ) for partition in self.windows_system.get_partitions()]

    def test_get_logical_disks(self) -> None:
        self.assertIsInstance(self.windows_system.get_logical_disks(), tuple)
        [self.assertIsInstance(
            logical_disk,
            LogicalDisk
        ) for logical_disk in self.windows_system.get_logical_disks()]
