import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from framework.utilities.os_utils.memory.memory_win import MemoryWindows
from framework.utilities.os_utils.memory.memory_linux import MemoryLinux


class MemoryUtilsAPI:
    def __init__(self, os_name, platform_obj):
        self.platform_obj = platform_obj
        self.os_name = os_name

        if self.os_name.lower() == "windows":
            self.__memory_utils_obj = MemoryWindows(self.platform_obj)
        elif self.os_name.lower() == "linux":
            self.__memory_utils_obj = MemoryLinux(self.platform_obj)
        else:
            raise ValueError(f"Unsupported OS: {self.os_name}")

    def size_and_info(self):
        return self.__memory_utils_obj.size_and_info()

    def rw_speed(self, size_mb):
        return self.__memory_utils_obj.rw_speed(size_mb)

    def stress_test(self, timeout_sec):
        return self.__memory_utils_obj.stress_test(timeout_sec)

    def integrity_test(self, size_mb):
        return self.__memory_utils_obj.integrity_test(size_mb)

    def leak_detect(self):
        return self.__memory_utils_obj.leak_detect()
