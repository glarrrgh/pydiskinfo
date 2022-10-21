from unittest import TestCase
from system import LogicalDisk
from windows_system import WindowsLogicalDisk


property_list = sorted(
    [
        'Description',
        'Device I.D.',
        'Type',
        'Filesystem',
        'Free Space',
        'Max Component Length',
        'Name',
        'Mounted',
        'Path',
        'Size',
        'Label',
        'Serial'
    ]
)


class LogicalDiskTests(TestCase):
    def test_has_all_properties(self) -> None:
        logical_disk = LogicalDisk(None)

        self.assertEqual(
            sorted(logical_disk.keys()),
            property_list
        )


class WindowsLogicalDiskTests(TestCase):
    def setUp(self) -> None:
        class FakeWmiLogicalDisk:
            def __init__(self) -> None:
                self.DeviceID = 'C:'
        self.fake_wmi_logical_disk = FakeWmiLogicalDisk()

    def test_has_all_properties(self) -> None:
        windows_logical_disk = WindowsLogicalDisk(None, None)
        self.assertEqual(
            sorted(windows_logical_disk),
            property_list
        )

    def test_get_device_id_etc(self) -> None:
        windows_logical_disk = WindowsLogicalDisk(
            self.fake_wmi_logical_disk,
            None
        )
        device_id, name, mounted = (
            windows_logical_disk.
            _get_device_id_name_mounted()
        )
        self.assertEqual(device_id, 'C:')
        self.assertEqual(name, 'C:')
        self.assertEqual(mounted, 'C:\\')
