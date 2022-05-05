from unittest import TestCase
from tests.fake_wmi import get_windows_system


class InterfaceTests(TestCase):
    """Test of programming interface"""
    def setUp(self) -> None:
        self.system = get_windows_system()

    def test_get_partitions(self) -> None:
        self.assertEqual(
            len(self.system.get_physical_disks()[0].get_partitions()),
            1
        )

    def test_get_system(self) -> None:
        self.assertIs(
            self.system.get_physical_disks()[0].get_system(),
            self.system
        )
