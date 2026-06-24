import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from framework.utilities.os_utils.storage.storage_linux import StorageLinux
from framework.utilities.os_utils.storage.storage_win import StorageWindows


class StorageUtilsAPI:
    def __init__(self, os_name, platform_obj):
        self.platform_obj = platform_obj
        self.os_name = os_name

        if self.os_name.lower() == "windows":
            self.__storage_utils_obj = StorageWindows(self.platform_obj)
        elif self.os_name.lower() == "linux":
            self.__storage_utils_obj = StorageLinux(self.platform_obj)
        else:
            raise ValueError(f"Unsupported OS: {self.os_name}")

    def check_disk_space(self):
        return self.__storage_utils_obj.check_disk_space()

    def test_sequential_read(self):
        return self.__storage_utils_obj.test_sequential_read()

    def test_sequential_write(self):
        return self.__storage_utils_obj.test_sequential_write()

    def test_random_read_write(self):
        return self.__storage_utils_obj.test_random_read_write()

    def test_data_integrity(self):
        return self.__storage_utils_obj.test_data_integrity()

    def test_repeated_write(self):
        return self.__storage_utils_obj.test_repeated_write()
