

class FakeWMILogicalDisk:
    device_id_number = 0

    def __init__(self) -> None:
        self.Description = 'Some description'
        self.DeviceID = f'device {FakeWMILogicalDisk.device_id_number}'
        FakeWMILogicalDisk.device_id_number += 1
        self.DriveType = 'Some type'
        self.FileSystem = 'Some filesystem'
        self.FreeSpace = '800000000'
        self.MaximumComponentLength = '255'
        self.Size = '1000000000'
        self.VolumeName = 'Some label'
        self.VolumeSerialNumber = 'Some serial'


class FakeWMIPartition:
    def __init__(self, logical_disks: list = None) -> None:
        self.BlockSize = '512'
        self.Bootable = True
        self.BootPartition = True
        self.Description = 'Some description'
        self.DeviceID = 'Some device id'
        self.DiskIndex = '0'
        self.Index = '0'
        self.NumberOfBlocks = '204800'
        self.PrimaryPartition = True
        self.Size = '104857600'
        self.StartingOffset = '1048576'
        self.Type = 'Some type'
        if logical_disks is None:
            self.set_logical_disks([FakeWMILogicalDisk()])
        else:
            self.set_logical_disks(logical_disks)

    def associators(self, association: str) -> list:
        return self.logical_disks

    def set_logical_disks(self, logical_disks: list) -> None:
        self.logical_disks = logical_disks

    def set_device_id(self, index, disk_index) -> None:
        self.DiskIndex = str(disk_index)
        self.Index = str(index)
        self.DeviceID = f'Partition {index} Disk {disk_index}'


class FakeWMIPhysicalDisk:
    disk_number = 0

    def __init__(self, partitions: list = None) -> None:
        self.Size = '256052966400'
        self.Index = str(FakeWMIPhysicalDisk.disk_number)
        FakeWMIPhysicalDisk.disk_number += 1
        self.DeviceID = 'Some device id'
        self.MediaType = 'Some media type'
        self.SerialNumber = 'Some serial'
        self.Model = 'Some model'
        self.TotalSectors = '500103450'
        self.TotalHeads = '255'
        self.TotalCylinders = '31130'
        self.BytesPerSector = '512'
        self.FirmWare = 'Some firmware'
        self.InterfaceType = 'Some interface'
        self.MediaLoaded = True
        self.Status = 'OK'
        if partitions is None:
            self.set_partitions([FakeWMIPartition()])
        else:
            self.set_partitions(partitions)

    def associators(self, association: str) -> list:
        return self.partitions

    def set_partitions(self, partitions: list) -> None:
        """Add another partition to the physical disk"""
        for partition_number, each_partition in enumerate(partitions):
            each_partition.set_device_id(partition_number, int(self.Index))
        self.partitions = partitions


class FakeWMIcursor:
    def __init__(self, physical_disks: list = None) -> None:
        if physical_disks is None:
            self.set_disks([FakeWMIPhysicalDisk()])
        else:
            self.set_disks(physical_disks)

    def Win32_DiskDrive(self) -> list:
        return self.physical_disks

    def set_disks(self, physical_disks: list) -> None:
        """Add another physical disk to the system"""
        self.physical_disks = physical_disks
