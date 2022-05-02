from unittest import TestCase
from src.pydiskinfo.partition import WindowsPartition


class TestWindowsPartition(TestCase):
    def setUp(self) -> None:
        class FakeWmiPartition:
            def __init__(self) -> None:
                self.PrimaryPartition = 1
        self.fake_wmi_partition = FakeWmiPartition()

    def test_get_primary_partition(self) -> None:
        partition = WindowsPartition(self.fake_wmi_partition, None)
        primary = partition._get_primary_partition()
        self.assertIs(primary, True)
