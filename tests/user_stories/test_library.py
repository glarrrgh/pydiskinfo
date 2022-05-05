from unittest import TestCase
from unittest.mock import patch
from src.pydiskinfo.system import create_system, WindowsSystem
from tests.fake_wmi import FakeWMIcursor


class PydiskinfoModuleTest(TestCase):
    """User story about developer using the module"""
    def test_module_windows(self) -> None:
        '''User stories about the module "interface" on a windows system'''
        # Mary generates a System object on a windows system
        with patch(
            target='sys.platform',
            new='win32'
        ), patch(
            target='wmi.WMI',
            new=FakeWMIcursor
        ), patch(
            target='socket.gethostname',
        ) as gethostname, patch(
            target='src.pydiskinfo.system.platform'
        ) as platform_mock:
            gethostname.return_value = 'testsystem'
            platform_mock.system.return_value = 'win32'
            platform_mock.win32_edition.return_value = 'test'
            platform_mock.win32_ver.return_value = [None, '0.1']
            system = create_system()
        self.assertIsInstance(system, WindowsSystem)

        # Mary tries to access some parameters from the system
        self.assertEqual(system['Name'], 'testsystem')
        self.assertEqual(system['Type'], 'win32')
        self.assertEqual(system['Version'], 'test 0.1')

        # Mary creates a new system with a name, and checks if the name is
        # stored correctly
        with patch(
            target='sys.platform',
            new='win32'
        ), patch(
            target='wmi.WMI',
            new=FakeWMIcursor
        ), patch(
            target='socket.gethostname',
        ) as gethostname, patch(
            target='src.pydiskinfo.system.platform'
        ) as platform_mock:
            gethostname.return_value = 'testsystem'
            platform_mock.system.return_value = 'win32'
            platform_mock.win32_edition.return_value = 'test'
            platform_mock.win32_ver.return_value = [None, '0.1']
            system = create_system(name='Marys System')
        self.assertEqual(system['Name'], 'Marys System')

        # Mary checks how many disks, partitions and logical disks there are
        # in her system
        self.assertEqual(len(system.get_physical_disks()), 1)
        self.assertEqual(len(system.get_partitions()), 1)
        self.assertEqual(len(system.get_logical_disks()), 1)

        # Mary checks how many partitions are under the first physical disk
        physical_disk = system.get_physical_disks()[0]

        self.assertEqual(
            len(physical_disk.get_partitions()),
            1
        )

        # Mary then checks how many logical disks that are attatched to
        # that partition
        partition = physical_disk.get_partitions()[0]
        self.assertEqual(
            len(partition.get_logical_disks()),
            1
        )

    # def test_module_linux(self) -> None:
    #     '''User stories about a module "interface" on a linux system'''
    #     # Mary generates a System object on a linux system
    #     with patch(
    #         target='sys.platform',
    #         new='linux'
    #     ), patch(
    #         target='wmi.WMI',
    #         new=FakeWMIcursor
    #     ):
    #         system = create_system()
    #     self.assertIsInstance(system, LinuxSystem)
