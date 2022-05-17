from unittest import TestCase
from src.pydiskinfo.windows_system import WindowsSystem
from tests.fake_wmi import get_windows_system


class PydiskinfoModuleTest(TestCase):
    """User story about developer using the module"""
    def test_module_windows(self) -> None:
        '''User stories about the module "interface" on a windows system'''
        # Mary generates a System object on a windows system
        system = get_windows_system()
        self.assertIsInstance(system, WindowsSystem)

        # Mary tries to access some parameters from the system
        self.assertEqual(system['Name'], 'Some system')
        self.assertEqual(system['Type'], 'Some type')
        self.assertEqual(system['Version'], 'test 10')

        # Mary creates a new system with a name, and checks if the name is
        # stored correctly
        system = get_windows_system(name='Marys System')
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

        # Mary then checks how many logical disks are attatched to
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
