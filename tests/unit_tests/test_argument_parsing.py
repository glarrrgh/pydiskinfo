from unittest import TestCase
from unittest.mock import patch
from tests.fake_wmi import get_windows_system
from src.pydiskinfo.argument_parsing import get_arguments, SanitizedArguments


class TestGetArguments(TestCase):
    def test_default_get_arguments(self) -> None:
        with patch('sys.argv', [
            'pydiskinfo',
        ]):
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
            ['Label', 'Filesystem', 'Free Space']
        )
        self.assertEqual(sanitized_arguments.system_name, '')
        self.assertFalse(sanitized_arguments.list_from_partitions)
        self.assertTrue(sanitized_arguments.physical_disk_size_human_readable)
        self.assertTrue(sanitized_arguments.partition_size_human_readable)
        self.assertFalse(sanitized_arguments.logical_disk_size_human_readable)

    def test_all_get_arguments(self) -> None:
        with patch('sys.argv', [
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
        ]):
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

    def test_pydiskinfo_class_keys(self) -> None:
        with patch('sys.argv', [
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
        ]):
            sanitized_arguments = get_arguments()
        system = get_windows_system()
        self.assertCountEqual(
            sanitized_arguments.physical_disk_options,
            system.get_physical_disks()[0].keys()
        )
        self.assertCountEqual(
            sanitized_arguments.partition_options,
            system.get_partitions()[0].keys()
        )
        self.assertCountEqual(
            sanitized_arguments.logical_disk_options,
            system.get_logical_disks()[0].keys()
        )


class TestSanitizedArgumentsClass(TestCase):
    """Tests for class SanitizedArguments"""
    def test_defautls_physical_disk_options(self) -> None:
        """Test that a default SanitizedArguments produces a property
        physical_disk_options of type list"""
        self.assertEqual(
            SanitizedArguments().physical_disk_options, []
        )

    def test_defaults_logical_disk_options(self) -> None:
        """Test that a default SanitizedArguments produces a property
        logical_disk_options of type list"""
        self.assertEqual(
            SanitizedArguments().logical_disk_options, []
        )

    def test_defautls_partition_options(self) -> None:
        """Test that a default SanitizedArguments produces a property
        partition_options of type list"""
        self.assertEqual(
            SanitizedArguments().partition_options, []
        )

    def test_defautls_logical_disk_orientation(self) -> None:
        """Test that a default SanitizedArguments produces a property
        logical_disk_orientation and set it to False"""
        self.assertFalse(SanitizedArguments().logical_disk_orientation)

    def test_defautls_physical_disk_list_partitions(self) -> None:
        """Test that a default SanitizedArguments produces a property
        physical_disk_list_partitions and set it to False"""
        self.assertFalse(SanitizedArguments().physical_disk_list_partitions)

    def test_defautls_partition_list_logical_disks(self) -> None:
        """Test that a default SanitizedArguments produces a property
        partition_list_logical_disks and set it to False"""
        self.assertFalse(SanitizedArguments().partition_list_logical_disks)

    def test_defautls_partition_show_physical_disk(self) -> None:
        """Test that a default SanitizedArguments produces a property
        partition_show_physical_disk and set it to False"""
        self.assertFalse(SanitizedArguments().partition_show_physical_disk)

    def test_defautls_logical_disk_list_partitions(self) -> None:
        """Test that a default SanitizedArguments produces a property
        logical_disk_list_partitions and set it to False"""
        self.assertFalse(SanitizedArguments().logical_disk_list_partitions)

    def test_defautls_list_from_partitions(self) -> None:
        """Test that a default SanitizedArguments produces a property
        list_from_partitions and set it to False"""
        self.assertFalse(SanitizedArguments().list_from_partitions)

    def test_defautls_system_name(self) -> None:
        """Test that a default SanitizedArguments produces a property
        system_name and set it to ''"""
        self.assertEqual(SanitizedArguments().system_name, '')

    def test_parse_dp_setting_physical_disk_size_human_readable(self) -> None:
        """if _parse_dp set physical_disk_size_human_readable"""
        self.assertFalse(
            SanitizedArguments().physical_disk_size_human_readable
        )
        self.assertFalse(
            SanitizedArguments({'dp': 'S'}).physical_disk_size_human_readable
        )
        self.assertTrue(
            SanitizedArguments({'dp': 's'}).physical_disk_size_human_readable
        )

    def test_parse_dp(self) -> None:
        """Test dp parsing returns the correct values"""
        self.assertEqual(
            SanitizedArguments()._parse_dp(''),
            ([], False, False)
        )
        self.assertEqual(
            SanitizedArguments()._parse_dp('PXSsipdtnmcbhCfIMa'),
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
        self.assertEqual(
            SanitizedArguments()._parse_pp(''),
            ([], False, False, False)
        )
        self.assertEqual(
            SanitizedArguments()._parse_pp('LXDbBoxpidNcrsSet'),
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
        self.assertFalse(
            SanitizedArguments().partition_size_human_readable
        )
        self.assertFalse(
            SanitizedArguments({'pp': 'S'}).partition_size_human_readable
        )
        self.assertTrue(
            SanitizedArguments({'pp': 's'}).partition_size_human_readable
        )

    def test_parse_lp(self) -> None:
        self.assertEqual(
            SanitizedArguments()._parse_lp(''),
            ([], False, False)
        )
        self.assertEqual(
            SanitizedArguments()._parse_lp('PXxdtfFUpvMsSVn'),
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
        self.assertFalse(
            SanitizedArguments().logical_disk_size_human_readable
        )
        self.assertFalse(
            SanitizedArguments({'lp': 'S'}).logical_disk_size_human_readable
        )
        self.assertTrue(
            SanitizedArguments({'lp': 's'}).logical_disk_size_human_readable
        )

    def test_list_from_partitions(self) -> None:
        """Test that a SanitizedArguments produces a property
        list_from_partitions and set it correctly"""
        self.assertTrue(SanitizedArguments({'p': True}).list_from_partitions)

    def test_system_name(self) -> None:
        """Test that a SanitizedArguments produces a property
        system_name and set it correctly ''"""
        sanitized_arguments = SanitizedArguments({'n': 'Some system'})
        self.assertEqual(sanitized_arguments.system_name, 'Some system')

    def test_argument_properties_against_WindowsPhysicalDisk(self) -> None:
        """Test that arguments give the same keys as PhysicalDisk"""
        self.assertEqual(
            sorted(
                SanitizedArguments({
                    'dp': 'sidptnmcbhCfIMa'
                }).physical_disk_options
            ),
            sorted(get_windows_system().get_physical_disks()[0].keys())
        )

    def test_argument_properties_against_WindowsPartition(self) -> None:
        """Test that arguments give the same keys as Partition"""
        self.assertEqual(
            sorted(
                SanitizedArguments({'pp': 'bBoxpdiNcrset'}).partition_options
            ),
            sorted(get_windows_system().get_partitions()[0].keys())
        )

    def test_argument_properties_against_WindowsLogicalDisk(self) -> None:
        """Test that arguments give the same keys as LogicalDisk"""
        self.assertEqual(
            sorted(
                SanitizedArguments({'lp': 'xdtfFUvMpsVn'}).logical_disk_options
            ),
            sorted(get_windows_system().get_logical_disks()[0].keys())
        )
