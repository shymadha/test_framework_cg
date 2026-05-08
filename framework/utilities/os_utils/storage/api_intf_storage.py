import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from framework.utilities.os_utils.storage.storage_win import StorageWindows
from framework.utilities.os_utils.storage.storage_linux import StorageLinux


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

    def sequential_write(self, file_path, size_mb):
        return self.__storage_utils_obj.sequential_write(file_path, size_mb)

    def sequential_read(self, file_path):
        return self.__storage_utils_obj.sequential_read(file_path)

    def random_rw(self, file_path, size_mb):
        return self.__storage_utils_obj.random_rw(file_path, size_mb)

    def data_integrity(self, file_path):
        return self.__storage_utils_obj.data_integrity(file_path)

    def disk_space(self, drive_or_mount=None):
        if drive_or_mount is None:
            drive_or_mount = "C:" if self.os_name.lower() == "windows" else "/"
        return self.__storage_utils_obj.disk_space(drive_or_mount)

    def repeated_write(self, file_path, size_mb, cycles):
        return self.__storage_utils_obj.repeated_write(file_path, size_mb, cycles)
