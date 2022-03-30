import re

import wmi


class Disk(object):
    """Contains information about physical and logical disks device like raid
        or spanned devices (not partitons).
        """

    def __init__(self, physical_disk: wmi._wmi_object) -> None:
        try:
            self.size = int(physical_disk.Size)
        except ValueError:
            self.size = -1
        try:
            self.path = physical_disk.DeviceID
            self.disk_number = int(self.path.split('PHYSICALDRIVE')[-1])
        except IndexError:
            self.path = ""
            self.disk_number = -1
        except ValueError:
            self.path = ""
            self.disk_number = -1
        self.media_type = physical_disk.MediaType
        self.caption = physical_disk.Caption


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

    def __str__(self) -> str:
        """Overloading the string method"""
        return ", ".join((self.get_caption(), self.get_path(), self.get_type(), self.get_size()))

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
        self.path = 

    def get_path(self) -> str:
        """Get a path usable for raw access."""
        pass

    def get_size(self) -> int:
        """Get the partition size in bytes."""
        pass

    def get_partiton_table_type(self) -> str:
        """get the partition table type"""

    def get_filesystem_type(self):
        """Get partition type."""
        pass

    def _set_labels(self, partition: wmi._wmi_object) -> None:
        """Private method that parse the logical disks"""
        self.labels = [ each_label.Name for each_label in partition.associators('Win32_LogicalDiskToPartition')]
        



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
    disks = []
    for physical_disk in wmi_cursor.Win32_DiskDrive():
        disks.append(Disk(physical_disk))
    return disks


if __name__ == "__main__":
    disks = get_disks()
    for each_disk in disks:
        print(each_disk)
