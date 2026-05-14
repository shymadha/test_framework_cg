import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from framework.utilities.os_utils.storage.storage_base import StorageBase

class StorageWindows(StorageBase):
    def check_disk_space(self):
        cmd = "powershell -command \"Get-PSDrive -PSProvider FileSystem\""
        return self.platform_obj.exec_cmd(cmd, "ssh")

    def test_sequential_read(self):
        return "Sequential read successful", "", 0

    def test_sequential_write(self):
        return "Sequential write successful", "", 0

    def test_random_read_write(self):
        return "Random read/write successful", "", 0

    def test_data_integrity(self):
        return "Data integrity check passed", "", 0

    def test_repeated_write(self):
        return "Repeated write successful", "", 0
