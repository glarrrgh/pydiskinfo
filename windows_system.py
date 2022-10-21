import platform
import wmi
from system import System, LogicalDisk, PhysicalDisk, Partition
from exceptions import PyDiskInfoParseError


class WindowsSystem(System):
    """This is the win32 version of the System class.

    This class will take care of the special cases when the module is runnning
    on windows."""

    def __init__(self, name: str = None) -> None:
        super().__init__(name)
        self._set_version()
        self['Type'] = 'Windows'

    def _set_version(self):
        self['Version'] = (
            f'{platform.win32_edition()} {platform.win32_ver()[1]}'
        )

    def _add_logical_disks(
        self,
        wmi_partition: wmi._wmi_object,
        partition: Partition
    ) -> None:
        for each_logical_disk in wmi_partition.associators(
            'Win32_LogicalDiskToPartition'
        ):
            logical_disk = self._add_logical_disk(
                WindowsLogicalDisk(each_logical_disk, self)
            )
            logical_disk.add_partition(partition)
            partition.add_logical_disk(logical_disk)

    def _add_partitions(
        self,
        wmi_disk: wmi._wmi_object,
        disk: PhysicalDisk
    ) -> None:
        for each_partition in wmi_disk.associators(
            'Win32_DiskDriveToDiskPartition'
        ):
            partition = self._add_partition(
                WindowsPartition(each_partition, disk)
            )
            disk.add_partition(partition)
            self._add_logical_disks(each_partition, partition)

    def _parse_system(self) -> None:
        """Parse the system"""
        try:
            cursor: wmi._wmi_namespace = wmi.WMI()
        except wmi.x_access_denied as err:
            raise PyDiskInfoParseError('Access to wmi is denied.') from err
        except wmi.x_wmi_authentication as err:
            raise PyDiskInfoParseError(
                'Authentication error when opening wmi'
            ) from err
        for each_disk in cursor.Win32_DiskDrive():
            disk = WindowsPhysicalDisk(each_disk, self)
            self._physical_disks.append(disk)
            self._add_partitions(each_disk, disk)


class WindowsPhysicalDisk(PhysicalDisk):
    """Subclass of PhysicalDrive that handles special windows situations"""
    def __init__(self, wmi_physical_disk: object, system: object) -> None:
        super().__init__(system)
        self._set_size(wmi_physical_disk)
        self._set_disk_number(wmi_physical_disk)
        self._set_device_id_and_path(wmi_physical_disk)
        self._set_media_type(wmi_physical_disk)
        self._set_serial_number(wmi_physical_disk)
        self._set_model(wmi_physical_disk)
        self._set_sectors(wmi_physical_disk)
        self._set_heads(wmi_physical_disk)
        self._set_cylinders(wmi_physical_disk)
        self._set_bytes_per_sector(wmi_physical_disk)
        self._set_firmware(wmi_physical_disk)
        self._set_interface_type(wmi_physical_disk)
        self._set_media_loaded(wmi_physical_disk)
        self._set_status(wmi_physical_disk)

    def _set_size(self, wmi_physical_disk: wmi._wmi_object) -> None:
        """set size of disk in bytes."""
        try:
            self['Size'] = int(wmi_physical_disk.Size)
        except ValueError:
            self['Size'] = -1

    def _set_disk_number(self, wmi_physical_disk: wmi._wmi_object) -> None:
        """set system disk identification number"""
        try:
            self['Disk Number'] = int(wmi_physical_disk.Index)
        except ValueError:
            self['Disk Number'] = -1

    def _set_device_id_and_path(
        self,
        wmi_physical_disk: wmi._wmi_object
    ) -> None:
        try:
            self['Path'] = wmi_physical_disk.DeviceID
            self['Device I.D.'] = self['Path']
        except AttributeError:
            self['Path'] = ""
            self['Device I.D.'] = ""

    def _set_media_type(self, wmi_physical_disk: wmi._wmi_object) -> None:
        try:
            self['Media'] = wmi_physical_disk.MediaType
        except AttributeError:
            self['Media'] = ""

    def _set_serial_number(self, wmi_physical_disk: wmi._wmi_object) -> None:
        try:
            self['Serial'] = wmi_physical_disk.SerialNumber
        except AttributeError:
            self['Serial'] = ""

    def _set_model(self, wmi_physical_disk: wmi._wmi_object) -> None:
        try:
            self['Model'] = wmi_physical_disk.Model
        except AttributeError:
            self['Model'] = ""

    def _set_sectors(self, wmi_physical_disk: wmi._wmi_object) -> None:
        """Set total number of sectors, or -1 if not a number."""
        try:
            self['Sectors'] = int(wmi_physical_disk.TotalSectors)
        except ValueError:
            self['Sectors'] = -1

    def _set_heads(self, wmi_physical_disk: wmi._wmi_object) -> None:
        """Set total number of heads, or -1 if not a number"""
        try:
            self['Heads'] = int(wmi_physical_disk.TotalHeads)
        except ValueError:
            self['Heads'] = -1

    def _set_cylinders(self, wmi_physical_disk: wmi._wmi_object) -> None:
        """Set total number of cylinders, or -1 if not a number"""
        try:
            self['Cylinders'] = int(wmi_physical_disk.TotalCylinders)
        except ValueError:
            self['Cylinders'] = -1

    def _set_bytes_per_sector(
        self,
        wmi_physical_disk: wmi._wmi_object
    ) -> None:
        """Set bytes per sector, or -1 if not a number"""
        try:
            self['Bytes per Sector'] = int(wmi_physical_disk.BytesPerSector)
        except ValueError:
            self['Bytes per Sector'] = -1

    def _set_firmware(self, wmi_physical_disk: wmi._wmi_object) -> None:
        """Set firmware"""
        try:
            self['Firmware'] = wmi_physical_disk.FirmWare
        except AttributeError:
            self['Firmware'] = "Unspecified"

    def _set_interface_type(
        self,
        wmi_physical_disk: wmi._wmi_object
    ) -> None:
        try:
            self['Interface'] = wmi_physical_disk.InterfaceType
        except AttributeError:
            self['Interface'] = ""

    def _set_media_loaded(self, wmi_physical_disk: wmi._wmi_object) -> None:
        try:
            self['Media Loaded'] = wmi_physical_disk.MediaLoaded
        except AttributeError:
            self['Media Loaded'] = False

    def _set_status(self, wmi_physical_disk: wmi._wmi_object) -> None:
        try:
            self['Status'] = wmi_physical_disk.Status
        except AttributeError:
            self['Status'] = ""


class WindowsPartition(Partition):
    def __init__(
        self,
        partition: wmi._wmi_object,
        disk: PhysicalDisk
    ) -> None:
        super().__init__(disk)
        self._wmi_partition = partition
        self._set_blocksize(partition)
        self._set_bootable(partition)
        self._set_active(partition)
        self._set_description(partition)
        self._set_device_id(partition)
        self._set_disk_number(partition)
        self._set_partition_number(partition)
        self._set_number_of_blocks(partition)
        self['Primary'] = self._get_primary_partition()
        self._set_size(partition)
        self._set_starting_offset(partition)
        self._set_type(partition)

    def _set_blocksize(self, partition: wmi._wmi_object) -> None:
        """Set blocksize or -1 if it fails."""
        try:
            self['Blocksize'] = int(partition.BlockSize)
        except AttributeError:
            self['Blocksize'] = -1
        except ValueError:
            self['Blocksize'] = -1

    def _set_bootable(self, partition: wmi._wmi_object) -> None:
        """Set bootable or false if it fails."""
        try:
            self['Bootable'] = partition.Bootable
        except AttributeError:
            self['Bootable'] = False

    def _set_active(self, partition: wmi._wmi_object) -> None:
        """Set if system boot partition, or False if it fails."""
        try:
            self['Active'] = partition.BootPartition
        except AttributeError:
            self['Active'] = False

    def _set_description(self, partition: wmi._wmi_object) -> None:
        """set a description provided by the system."""
        try:
            self['Description'] = partition.Description
        except AttributeError:
            self['Description'] = ""

    def _set_device_id(self, partition: wmi._wmi_object) -> None:
        """set the device id provided by the system."""
        try:
            self['Device I.D.'] = partition.DeviceID
        except AttributeError:
            self['Device I.D.'] = ""

    def _set_disk_number(self, partition: wmi._wmi_object) -> None:
        """Set the disk index number as the system sees it."""
        try:
            self['Disk Number'] = int(partition.DiskIndex)
        except AttributeError:
            self['Disk Number'] = -1
        except ValueError:
            self['Disk Number'] = -1

    def _set_partition_number(self, partition: wmi._wmi_object) -> None:
        """Set the partition index on the disk, according to the system."""
        try:
            self['Partition Number'] = int(partition.Index)
        except AttributeError:
            self['Partition Number'] = -1
        except ValueError:
            self['Partition Number'] = -1

    def _set_number_of_blocks(self, partition: wmi._wmi_object) -> None:
        """Set number of blocks."""
        try:
            self['Blocks'] = int(partition.NumberOfBlocks)
        except AttributeError:
            self['Blocks'] = -1
        except ValueError:
            self['Blocks'] = -1

    def _get_primary_partition(self) -> None:
        """Set if the partition is a primary partition"""
        try:
            primary = self._wmi_partition.PrimaryPartition
        except AttributeError:
            primary = False
        return primary

    def _set_size(self, partition: wmi._wmi_object) -> None:
        """Set partition size in bytes."""
        try:
            self['Size'] = int(partition.Size)
        except AttributeError:
            self['Size'] = 0
        except ValueError:
            self['Size'] = 0

    def _set_starting_offset(self, partition: wmi._wmi_object) -> None:
        """Set partition starting offset in bytes."""
        try:
            self['Offset'] = int(partition.StartingOffset)
        except AttributeError:
            self['Offset'] = -1
        except ValueError:
            self['Offset'] = -1

    def _set_type(self, partition: wmi._wmi_object) -> None:
        """Set partition type."""
        try:
            self['Type'] = partition.Type
        except AttributeError:
            self['Type'] = ""


class WindowsLogicalDisk(LogicalDisk):
    _DRIVETYPES = [
        'Unknown',
        'No Root Directory',
        'Removable Disk',
        'Local Disk',
        'Network Drive',
        'Compact Disk',
        'RAM Disk'
    ]

    def __init__(
        self,
        logical_disk: wmi._wmi_object,
        system: System
    ) -> None:
        super().__init__(system)
        self._wmi_logical_disk = logical_disk
        self._set_description(logical_disk)
        self['Device I.D.'], self['Name'], self['Mounted'] = (
            self._get_device_id_name_mounted()
        )
        self._set_drive_type(logical_disk)
        self._set_file_system(logical_disk)
        self._set_free_space(logical_disk)
        self._set_maximum_component_length(logical_disk)
        self._set_size(logical_disk)
        self._set_volume_name(logical_disk)
        self._set_volume_serial_number(logical_disk)

    def _set_description(self, logical_disk: wmi._wmi_object) -> None:
        """Set the description"""
        try:
            self['Description'] = logical_disk.Description
            if not type(self['Description']) == str:
                self['Description'] = ""
        except AttributeError:
            self['Description'] = ""

    def _get_device_id_name_mounted(self) -> None:
        """Set the unique device ID and name. On windows
        this is pretty much the same as path.
        """
        try:
            device_id = self._wmi_logical_disk.DeviceID
            if not type(device_id) == str:
                device_id = ''
        except AttributeError:
            device_id = ''
        name = device_id
        mounted = device_id + '\\'
        return device_id, name, mounted

    def _set_drive_type(self, logical_disk: wmi._wmi_object) -> None:
        """Set the drive type."""
        try:
            drivetype = int(logical_disk.DriveType)
        except AttributeError:
            drivetype = 0
        except ValueError:
            drivetype = 0
        try:
            self['Type'] = self._DRIVETYPES[drivetype]
        except IndexError:
            self['Type'] = self._DRIVETYPES[0]

    def _set_file_system(self, logical_disk: wmi._wmi_object) -> None:
        """Set the filesystem according to the system."""
        try:
            self['Filesystem'] = logical_disk.FileSystem
            if type(self['Filesystem']) != str:
                self['Filesystem'] = "unknown"
        except AttributeError:
            self['Filesystem'] = "unknown"

    def _set_free_space(self, logical_disk: wmi._wmi_object) -> None:
        """Set the available space on the filesystem in bytes"""
        try:
            self['Free Space'] = int(logical_disk.FreeSpace)
        except AttributeError:
            self['Free Space'] = 0
        except ValueError:
            self['Free Space'] = 0
        except TypeError:
            self['Free Space'] = 0

    def _set_maximum_component_length(
        self,
        logical_disk: wmi._wmi_object
    ) -> None:
        """Set the max path length in characters."""
        try:
            self['Max Component Length'] = int(
                logical_disk.MaximumComponentLength
            )
        except AttributeError:
            self['Max Component Length'] = 0
        except ValueError:
            self['Max Component Length'] = 0
        except TypeError:
            self['Max Component Length'] = 0

    def _set_size(self, logical_disk: wmi._wmi_object) -> None:
        """Set the size in bytes."""
        try:
            self['Size'] = int(logical_disk.Size)
        except AttributeError:
            self['Size'] = 0
        except ValueError:
            self['Size'] = 0
        except TypeError:
            self['Size'] = 0

    def _set_volume_name(self, logical_disk: wmi._wmi_object) -> None:
        """Set the volume name. Usually the Label value."""
        try:
            self['Label'] = logical_disk.VolumeName
            if type(self['Label']) != str:
                self['Label'] = ""
        except AttributeError:
            self['Label'] = ""

    def _set_volume_serial_number(
        self,
        logical_disk: wmi._wmi_object
    ) -> None:
        """Set the volume serial number."""
        try:
            self['Serial'] = logical_disk.VolumeSerialNumber
            if type(self['Serial']) != str:
                self['Serial'] = ""
        except AttributeError:
            self['Serial'] = ""
