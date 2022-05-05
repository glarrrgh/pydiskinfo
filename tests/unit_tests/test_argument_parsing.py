from unittest import TestCase
from unittest.mock import patch
from src.pydiskinfo.system import System, create_system
from tests.fake_wmi import FakeWMIcursor
from src.pydiskinfo.argument_parsing import get_arguments, SanitizedArguments


class TestGetArguments(TestCase):
    @patch('sys.argv', [
        'pydiskinfo',
    ])
    def test_default_get_arguments(self) -> None:
        sanitized_arguments = get_arguments()
        self.assertIsInstance(sanitized_arguments, SanitizedArguments)
        self.assertFalse(sanitized_arguments.logical_disk_orientation)
        self.assertEqual(
            sanitized_arguments.physical_disk_options,
            ['Disk Number', 'Path', 'Media', 'Serial', 'Size']
        )
        self.assertEqual(
            sanitized_arguments.partition_options,
            ['Device I.D.', 'Type', 'Size', 'Offset']
        )
        self.assertEqual(
            sanitized_arguments.logical_disk_options,
            ['Path', 'Label', 'Filesystem', 'Free Space']
        )
        self.assertEqual(sanitized_arguments.system_name, '')
        self.assertFalse(sanitized_arguments.list_from_partitions)
        self.assertTrue(sanitized_arguments.physical_disk_size_human_readable)
        self.assertTrue(sanitized_arguments.partition_size_human_readable)
        self.assertFalse(sanitized_arguments.logical_disk_size_human_readable)

    @patch('sys.argv', [
        'pydiskinfo',
        '-dp',
        'PXSsidptnmcbhCfIMa',
        '-pp',
        'LXDbBoxpdiNcrSset',
        '-lp',
        'PXxdtfFUvpMSsVn',
        '-l',
        '-n',
        'Some system',
        '-p'
    ])
    def test_all_get_arguments(self) -> None:
        sanitized_arguments = get_arguments()
        self.assertIsInstance(sanitized_arguments, SanitizedArguments)
        self.assertTrue(sanitized_arguments.logical_disk_orientation)
        self.assertEqual(
            sanitized_arguments.physical_disk_options,
            [
                'Size',
                'Disk Number',
                'Device I.D.',
                'Path',
                'Media',
                'Serial',
                'Model',
                'Sectors',
                'Bytes per Sector',
                'Heads',
                'Cylinders',
                'Firmware',
                'Interface',
                'Media Loaded',
                'Status'
            ]
        )
        self.assertEqual(
            sanitized_arguments.partition_options,
            [
                'Blocksize',
                'Bootable',
                'Active',
                'Description',
                'Path',
                'Device I.D.',
                'Disk Number',
                'Partition Number',
                'Blocks',
                'Primary',
                'Size',
                'Offset',
                'Type'
            ]
        )
        self.assertEqual(
            sanitized_arguments.logical_disk_options,
            [
                'Description',
                'Device I.D.',
                'Type',
                'Filesystem',
                'Free Space',
                'Max Component Length',
                'Name',
                'Path',
                'Mounted',
                'Size',
                'Label',
                'Serial'
            ]
        )
        self.assertEqual(sanitized_arguments.system_name, 'Some system')
        self.assertTrue(sanitized_arguments.list_from_partitions)
        self.assertTrue(sanitized_arguments.physical_disk_size_human_readable)
        self.assertTrue(sanitized_arguments.partition_size_human_readable)
        self.assertTrue(sanitized_arguments.logical_disk_size_human_readable)


class TestSanitizedArgumentsClass(TestCase):
    """Tests for class SanitizedArguments"""
    def test_defautls_physical_disk_options(self) -> None:
        """Test that a default SanitizedArguments produces a property
        physical_disk_options of type list"""
        sanitized_arguments = SanitizedArguments()
        self.assertEqual(
            sanitized_arguments.physical_disk_options, []
        )

    def test_defaults_logical_disk_options(self) -> None:
        """Test that a default SanitizedArguments produces a property
        logical_disk_options of type list"""
        sanitized_arguments = SanitizedArguments()
        self.assertEqual(
            sanitized_arguments.logical_disk_options, []
        )

    def test_defautls_partition_options(self) -> None:
        """Test that a default SanitizedArguments produces a property
        partition_options of type list"""
        sanitized_arguments = SanitizedArguments()
        self.assertEqual(
            sanitized_arguments.partition_options, []
        )

    def test_defautls_logical_disk_orientation(self) -> None:
        """Test that a default SanitizedArguments produces a property
        logical_disk_orientation and set it to False"""
        sanitized_arguments = SanitizedArguments()
        self.assertFalse(sanitized_arguments.logical_disk_orientation)

    def test_defautls_physical_disk_list_partitions(self) -> None:
        """Test that a default SanitizedArguments produces a property
        physical_disk_list_partitions and set it to False"""
        sanitized_arguments = SanitizedArguments()
        self.assertFalse(sanitized_arguments.physical_disk_list_partitions)

    def test_defautls_partition_list_logical_disks(self) -> None:
        """Test that a default SanitizedArguments produces a property
        partition_list_logical_disks and set it to False"""
        sanitized_arguments = SanitizedArguments()
        self.assertFalse(sanitized_arguments.partition_list_logical_disks)

    def test_defautls_partition_show_physical_disk(self) -> None:
        """Test that a default SanitizedArguments produces a property
        partition_show_physical_disk and set it to False"""
        sanitized_arguments = SanitizedArguments()
        self.assertFalse(sanitized_arguments.partition_show_physical_disk)

    def test_defautls_logical_disk_list_partitions(self) -> None:
        """Test that a default SanitizedArguments produces a property
        logical_disk_list_partitions and set it to False"""
        sanitized_arguments = SanitizedArguments()
        self.assertFalse(sanitized_arguments.logical_disk_list_partitions)

    def test_defautls_list_from_partitions(self) -> None:
        """Test that a default SanitizedArguments produces a property
        list_from_partitions and set it to False"""
        sanitized_arguments = SanitizedArguments()
        self.assertFalse(sanitized_arguments.list_from_partitions)

    def test_defautls_system_name(self) -> None:
        """Test that a default SanitizedArguments produces a property
        system_name and set it to ''"""
        sanitized_arguments = SanitizedArguments()
        self.assertEqual(sanitized_arguments.system_name, '')

    def test_parse_dp_setting_physical_disk_size_human_readable(self) -> None:
        """if _parse_dp set physical_disk_size_human_readable"""
        sanitized_arguments = SanitizedArguments()
        self.assertFalse(
            sanitized_arguments.physical_disk_size_human_readable
        )
        sanitized_arguments = SanitizedArguments({'dp': 'S'})
        self.assertFalse(
            sanitized_arguments.physical_disk_size_human_readable
        )
        sanitized_arguments = SanitizedArguments({'dp': 's'})
        self.assertTrue(
            sanitized_arguments.physical_disk_size_human_readable
        )

    def test_parse_dp(self) -> None:
        """Test dp parsing returns the correct values"""
        sanitized_arguments = SanitizedArguments()
        self.assertEqual(
            sanitized_arguments._parse_dp(''),
            ([], False, False)
        )
        self.assertEqual(
            sanitized_arguments._parse_dp('PXSsipdtnmcbhCfIMa'),
            (
                [
                    'Size',
                    'Disk Number',
                    'Path',
                    'Device I.D.',
                    'Media',
                    'Serial',
                    'Model',
                    'Sectors',
                    'Bytes per Sector',
                    'Heads',
                    'Cylinders',
                    'Firmware',
                    'Interface',
                    'Media Loaded',
                    'Status'
                ],
                True,
                True
            )
        )

    def test_parse_pp(self) -> None:
        sanitized_arguments = SanitizedArguments()
        self.assertEqual(
            sanitized_arguments._parse_pp(''),
            ([], False, False, False)
        )
        self.assertEqual(
            sanitized_arguments._parse_pp('LXDbBoxpidNcrsSet'),
            (
                [
                    'Blocksize',
                    'Bootable',
                    'Active',
                    'Description',
                    'Path',
                    'Disk Number',
                    'Device I.D.',
                    'Partition Number',
                    'Blocks',
                    'Primary',
                    'Size',
                    'Offset',
                    'Type'
                ],
                True,
                True,
                False
            )
        )

    def test_parse_pp_setting_partition_size_human_readable(self) -> None:
        """if _parse_pp set physical_disk_size_human_readable"""
        sanitized_arguments = SanitizedArguments()
        self.assertFalse(
            sanitized_arguments.partition_size_human_readable
        )
        sanitized_arguments = SanitizedArguments({'pp': 'S'})
        self.assertFalse(
            sanitized_arguments.partition_size_human_readable
        )
        sanitized_arguments = SanitizedArguments({'pp': 's'})
        self.assertTrue(
            sanitized_arguments.partition_size_human_readable
        )

    def test_parse_lp(self) -> None:
        sanitized_arguments = SanitizedArguments()
        self.assertEqual(
            sanitized_arguments._parse_lp(''),
            ([], False, False)
        )
        self.assertEqual(
            sanitized_arguments._parse_lp('PXxdtfFUpvMsSVn'),
            (
                [
                    'Description',
                    'Device I.D.',
                    'Type',
                    'Filesystem',
                    'Free Space',
                    'Max Component Length',
                    'Path',
                    'Name',
                    'Mounted',
                    'Size',
                    'Label',
                    'Serial'
                ],
                True,  # list partitions
                False
            )
        )

    def test_parse_lp_setting_logical_disk_size_human_readable(self) -> None:
        """if _parse_pp set physical_disk_size_human_readable"""
        sanitized_arguments = SanitizedArguments()
        self.assertFalse(
            sanitized_arguments.logical_disk_size_human_readable
        )
        sanitized_arguments = SanitizedArguments({'lp': 'S'})
        self.assertFalse(
            sanitized_arguments.logical_disk_size_human_readable
        )
        sanitized_arguments = SanitizedArguments({'lp': 's'})
        self.assertTrue(
            sanitized_arguments.logical_disk_size_human_readable
        )

    def test_list_from_partitions(self) -> None:
        """Test that a SanitizedArguments produces a property
        list_from_partitions and set it correctly"""
        sanitized_arguments = SanitizedArguments({'p': True})
        self.assertTrue(sanitized_arguments.list_from_partitions)

    def test_system_name(self) -> None:
        """Test that a SanitizedArguments produces a property
        system_name and set it correctly ''"""
        sanitized_arguments = SanitizedArguments({'n': 'Some system'})
        self.assertEqual(sanitized_arguments.system_name, 'Some system')

    def test_argument_properties_against_WindowsPhysicalDisk(self) -> None:
        """Test that arguments give the same keys as PhysicalDisk"""
        with patch(
            'wmi.WMI',
            FakeWMIcursor
        ), patch(
            'sys.platform',
            'win32'
        ):
            system = create_system()
        sanitized_arguments = SanitizedArguments({'dp': 'sidptnmcbhCfIMa'})
        self.assertEqual(
            sorted(sanitized_arguments.physical_disk_options),
            sorted(system.get_physical_disks()[0].keys())
        )

    def test_argument_properties_against_WindowsPartition(self) -> None:
        """Test that arguments give the same keys as Partition"""
        with patch(
            'wmi.WMI',
            FakeWMIcursor
        ), patch(
            'sys.platform',
            'win32'
        ):
            system = create_system()
        sanitized_arguments = SanitizedArguments({'pp': 'bBoxpdiNcrset'})
        self.assertEqual(
            sorted(
                sanitized_arguments.partition_options
            ),
            sorted(system.get_partitions()[0].keys())
        )

    def test_argument_properties_against_WindowsLogicalDisk(self) -> None:
        """Test that arguments give the same keys as LogicalDisk"""
        with patch(
            'wmi.WMI',
            FakeWMIcursor
        ), patch(
            'sys.platform',
            'win32'
        ):
            system = create_system()
        sanitized_arguments = SanitizedArguments({'lp': 'xdtfFUvMpsVn'})
        self.assertEqual(
            sorted(
                sanitized_arguments.logical_disk_options
                + ['System', 'Partitions']
            ),
            sorted(system.get_logical_disks()[0].keys())
        )
