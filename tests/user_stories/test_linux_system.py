from io import StringIO
from unittest.mock import patch, MagicMock, Mock
from unittest import TestCase
from src.pydiskinfo.linux_system import LinuxSystem, LinuxPartition
from src.pydiskinfo import create_system

file_data = {
    '/proc/partitions':
        'major\tminor\t#blocks\tname\n'
        '   8        0  976762584 sda\n'
        '   8        1  976759808 sda1\n'
        '   8       16 1953514584 sdb\n'
        '   8       17  976761856 sdb1\n'
        '   8       18  976750592 sdb2\n'
        '   8       48 1953514584 sdd\n'
        '   8       49     498688 sdd1\n'
        '   8       50  976761856 sdd2\n'
        '   8       51  976226304 sdd3\n'
        '   8       32  976762584 sdc\n'
        '   8       33  976759808 sdc1\n'
        '   9        0 2929883136 md0\n'
        ' 253        0  209715200 dm-0\n'
        ' 253        1    8388608 dm-1\n'
        ' 253        2 1734868992 dm-2\n'
        ' 253        3 2929881088 dm-3\n'
        ' 179        0   15558144 mmcblk0\n'
        ' 179        1     262144 mmcblk0p1\n'
        ' 179        2   15291904 mmcblk0p2\n'
}

df_output = (
    'Filesystem                    Type         1B-blocks         Avail '
    'Mounted on\n'
    'udev                          devtmpfs    4152942592    4152942592 '
    '/dev\n'
    'tmpfs                         tmpfs        833921024     815149056 '
    '/run\n'
    '/dev/sda1                     ext4      500101021696  197152677888 '
    '/\n'
    'tmpfs                         tmpfs       4169596928    4169596928 '
    '/dev/shm\n'
    'tmpfs                         tmpfs          5242880       5242880 '
    '/run/lock\n'
    'tmpfs                         tmpfs       4169596928    4169596928 '
    '/sys/fs/cgroup\n'
    '/dev/sdd1                     vfat         509640704     506204160 '
    '/boot/efi\n'
    'tmpfs                         tmpfs        833916928     833916928 '
    '/run/user/1000\n'
    '/dev/mmcblk0p2                ext4       15381823488   12274655232 '
    '/mnt/sdcard1'
    '/dev/mmcblk0p1                vfat         264289280     232720896 '
    '/mnt/sdcard2'
)


def file_open_sf(filename, mode) -> MagicMock:
    if filename == '/proc/partitions':
        result = MagicMock()
        result.__enter__.return_value = StringIO(file_data[filename])
        return result
    return MagicMock()


def subprocess_run_sf(
    arguments: tuple,
    capture_output: bool,
    text: bool
) -> Mock:
    if arguments[0] == 'df':
        mock = Mock()
        mock.stdout = df_output
        return mock
    return MagicMock()


def create_linux_system(name: str = None) -> LinuxSystem:
    if not name:
        name = 'Some system'
    with patch(
        'sys.platform',
        'linux'
    ), patch(
        'src.pydiskinfo.linux_system.open',
        side_effect=file_open_sf
    ), patch(
        'src.pydiskinfo.linux_system.subprocess.run',
        side_effect=subprocess_run_sf
    ), patch(
        'src.pydiskinfo.linux_system.os'
    ) as mock_os:
        mock_os.uname.return_value = ('Linux', '', '4.19.0-20-test')
        return create_system(name)


class LinuxSystemTests(TestCase):
    def test_linux_system(self) -> None:
        # Mary generates a System object on a linux system
        self.assertIsInstance(create_linux_system(), LinuxSystem)

        # Mary tries to access some parameters from the system
        system = create_linux_system()
        self.assertEqual(system['Name'], 'Some system')
        self.assertEqual(system['Type'], 'Linux')
        self.assertEqual(system['Version'], 'Linux 4.19.0-20-test')

        # Mary creates a new system with a name, and checks if the name is
        # stored correctly
        self.assertEqual(create_linux_system('Marys rpi')['Name'], 'Marys rpi')

        # Mary checks how many disks, partitions and logical disks there are
        # in her system
        self.assertEqual(len(system.get_physical_disks()), 4)
        self.assertEqual(len(system.get_partitions()), 7)
        self.assertEqual(len(system.get_logical_disks()), 2)

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
        