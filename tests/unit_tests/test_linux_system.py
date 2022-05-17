from io import StringIO
from unittest.mock import patch, MagicMock, Mock
from unittest import TestCase
from src.pydiskinfo.linux_system import LinuxSystem
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


class LinuxSystemTest(TestCase):
    def setUp(self) -> None:
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
            self.system = create_system('test system')

    def test_system_creation(self) -> None:
        self.assertIsInstance(self.system, LinuxSystem)
