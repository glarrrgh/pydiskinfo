

class FakeWMILogicalDisk:
    def __init__(self) -> None:
        pass


class FakeWMIPartition:
    def __init__(self) -> None:
        pass

    def associators(self, association: str) -> list:
        return [FakeWMILogicalDisk()]


class FakeWMIPhysicalDisk:
    def __init__(self) -> None:
        self.Size = '256052966400'
        self.Index = '0'
        self.TotalSectors = '500103450'
        self.TotalHeads = '255'
        self.TotalCylinders = '31130'
        self.BytesPerSector = '512'

    def associators(self, association: str) -> list:
        return [FakeWMIPartition()]


class FakeWMIcursor:
    def __init__(self) -> None:
        pass

    def Win32_DiskDrive(self) -> list:
        return [FakeWMIPhysicalDisk()]
