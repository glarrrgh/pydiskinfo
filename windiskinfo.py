import re

import wmi


class Disk(object):
    """Contains information about physical and logical disks device like raid
        or spanned devices (not partitons).
        """

    def __init__(self, physical_disk: wmi._wmi_object) -> None:
        self._disk = physical_disk
        self._set_size()
        self._set_path()
        self.media_type = physical_disk.MediaType
        self.caption = physical_disk.Caption
        self._set_partitions(physical_disk)


    def get_path(self) -> str:
        """Get a path usable for raw access."""
        return self.path

    def get_size(self) -> int:
        """Get the disk size in bytes."""
        return str(self.size)

    def is_removable(self) -> bool:
        """Get wether disk is removable"""
        if self.media_type == "Removable Media":
            return True
        return False

    def get_type(self) -> str:
        """Get the disk type"""
        return self.media_type

    def get_partitions(self) -> list:
        """Get a list of partition objects"""
        return self.partitions[:]

    def get_caption(self) -> str:
        """Get model name and maybe manufacturer"""
        return self.caption

    def _set_size(self) -> None:
        """private: extract size from a wmi object"""
        try:
            self.size = int(self._disk.Size)
        except ValueError:
            self.size = -1

    def _set_path(self) -> None:
        """private: extract the disk path from a wmi object"""
        try:
            self.path = self._disk.DeviceID
            self.disk_number = int(self.path.split('PHYSICALDRIVE')[-1])
        except IndexError:
            self.path = ""
            self.disk_number = -1
        except ValueError:
            self.path = ""
            self.disk_number = -1

    def __str__(self) -> str:
        """Overloading the string method"""
        disk = ", ".join((self.get_caption(), self.get_path(), self.get_type(), self.get_size()))
        partitions = ["\n".join(["    " + line for line in str(partition).split("\n")]) for partition in self.partitions]
        try:   
            return "\n".join( (disk, *partitions ) )
        except IndexError:
            return disk

    def _set_partitions(self, physical_disk: wmi._wmi_object) -> None:
        """Private method that parses the partitons"""
        self.partitions = [ Partition(each_partition) for each_partition in physical_disk.associators('Win32_DiskDriveToDiskPartition') ]


class Partition(object):
    """Contains information about partitions. This includes logical disk, 
    or 'volume' information. The same volume may span several disks, and the 
    filesystem of the partition, will in those cases be the filesystem of the 
    spanned volume. The partition may in that case not include a functional 
    filesystem on its own, though its contents will be part of one.
    """

    def __init__(self, partition) -> None:
        self._partition = partition
        self._set_volumes()
        self._set_size()
        self._set_partition_table_type()
        self._set_descriptor()

    def get_size(self) -> int:
        """Get the partition size in bytes."""
        return self.size

    def get_descriptor(self) -> str:
        """Get a descriptor of the partition"""
        return self.descriptor

    def get_partiton_table_type(self) -> str:
        """get the partition table type"""
        return self.partition_table_type

    def _set_descriptor(self) -> None:
        """private: extract partition descriptor from a wmi object"""
        self.descriptor = self._partition.Name

    def _set_volumes(self) -> None:
        """Private: parse the logical disks"""
        self.volumes = [ Volume(volume) for volume in self._partition.associators('Win32_LogicalDiskToPartition')]

    def _set_size(self) -> None:
        """private: extract size from a wmi object"""
        try:
            self.size = int(self._partition.Size)
        except ValueError:
            self.size = 0

    def _set_partition_table_type(self) -> None:
        """private: extract partition table type from a wmi object"""
        self.partition_table_type = self._partition.Type

    def __str__(self) -> str:
        """overloading the __str__ method"""
        partition = ", ".join((self.get_descriptor(), self.get_partiton_table_type(), str(self.get_size())))
        volumes = []
        volumes = ["\n".join(["    " + line for line in str(volume).split("\n")]) for volume in self.volumes]
        try:
            return "\n".join((partition, *volumes))
        except IndexError:
            return partition


class Volume(object):
    def __init__(self, volume) -> None:
        self._volume = volume
        self._set_name()
        self._set_filesystem()

    def get_file_system(self) -> str:
        """Get filesystem type"""
        return self.file_system

    def get_name(self) -> str:
        """Get the volume path letter."""
        return self.name

    def _set_filesystem(self) -> None:
        """Private: Extracts the filesystem type from a wmi object"""
        if isinstance(self._volume.FileSystem, str):
            self.file_system = self._volume.FileSystem
        else:
            self.file_system = ""

    def _set_name(self) -> None:
        """Private: Extracts the volume name from a wmi object"""
        if isinstance(self._volume.Name, str):
            self.name = self._volume.Name
        else:
            self.name = ""
    
    def __str__(self) -> str:
        """overloading the __str__ method"""
        return ", ".join((self.get_name(), self.get_file_system()))


def get_disks(computer: str = "", username: str = "", password: str = "") -> list:
    """Reads the system information and returns a list of disk information.
    The list consist of Disk objects. The Disk object will include the partiton
    objects

    You may supply computer, username and password to connect to other
    computers. But no concideration is taken for the protection of credentials
    in memory. Username need to include domain/workgroup. Like domain\\username
    """
    try:
        wmi_cursor = wmi.WMI(computer=computer, user=username, password=password)
    except wmi.x_access_denied as err:
        return None
    except wmi.x_wmi_authentication as err:
        return None
    disks = [Disk(physical_disk) for physical_disk in wmi_cursor.Win32_DiskDrive()]
    return disks


if __name__ == "__main__":
    disks = get_disks()
    for each_disk in disks:
        print(each_disk)
