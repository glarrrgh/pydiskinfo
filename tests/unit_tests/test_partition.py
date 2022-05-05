from unittest import TestCase
from src.pydiskinfo.partition import WindowsPartition
from tests.fake_wmi import get_windows_system


class TestWindowsPartition(TestCase):
    def setUp(self) -> None:
        class FakeWmiPartition:
            def __init__(self) -> None:
                self.PrimaryPartition = True
        self.fake_wmi_partition = FakeWmiPartition()

    def test_get_primary_partition(self) -> None:
        partition = WindowsPartition(self.fake_wmi_partition, None)
        primary = partition._get_primary_partition()
        self.assertIs(primary, True)


class InterfaceTests(TestCase):
    def setUp(self) -> None:
        self.system = get_windows_system()

    def test_get_logical_disks(self) -> None:
        self.assertEqual(
            len(
                self.system
                .get_physical_disks()[0]
                .get_partitions()[0]
                .get_logical_disks()
            ),
            1
        )

    def test_get_physical_disk(self) -> None:
        self.assertIs(
            self.system
            .get_physical_disks()[0]
            .get_partitions()[0]
            .get_physical_disk(),
            self.system.get_physical_disks()[0]
        )
