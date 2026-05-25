# import sys
# import os

# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# from framework.utilities.os_utils.memory.memory_win import MemoryWindows
# from framework.utilities.os_utils.memory.memory_linux import MemoryLinux

# class MemoryUtilsAPI:
#     def __init__(self, os_name, platform_obj):
#         self.platform_obj = platform_obj
#         self.os_name = os_name

#         if self.os_name.lower() == "windows":
#             self.__memory_utils_obj = MemoryWindows(self.platform_obj)
#         elif self.os_name.lower() == "linux":
#             self.__memory_utils_obj = MemoryLinux(self.platform_obj)
#         else:
#             raise ValueError(f"Unsupported OS: {self.os_name}")

#     def test_ram_size_info(self):
#         return self.__memory_utils_obj.test_ram_size_info()

#     def test_ram_rw_speed(self):
#         return self.__memory_utils_obj.test_ram_rw_speed()

#     def test_ram_stress(self):
#         return self.__memory_utils_obj.test_ram_stress()

#     def test_ram_integrity(self):
#         return self.__memory_utils_obj.test_ram_integrity()

#     def test_memory_leak_detect(self):
#         return self.__memory_utils_obj.test_memory_leak_detect()


import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from framework.utilities.os_utils.memory.memory_win import MemoryWindows
from framework.utilities.os_utils.memory.memory_linux import MemoryLinux

class MemoryUtilsAPI:
    """
    Unified interface for memory-related test utilities.
    Dispatches to OS-specific implementations (Windows/Linux).
    """

    def __init__(self, os_name, platform_obj):
        self.platform_obj = platform_obj
        self.os_name = os_name.lower()

        if self.os_name == "windows":
            self._memory_utils_obj = MemoryWindows(self.platform_obj)
        elif self.os_name == "linux":
            self._memory_utils_obj = MemoryLinux(self.platform_obj)
        else:
            raise ValueError(f"Unsupported OS: {self.os_name}")

    def test_ram_size_info(self):
        return self._memory_utils_obj.test_ram_size_info()

    def test_ram_rw_speed(self):
        return self._memory_utils_obj.test_ram_rw_speed()

    def test_ram_stress(self):
        return self._memory_utils_obj.test_ram_stress()

    def test_ram_integrity(self):
        return self._memory_utils_obj.test_ram_integrity()

    def test_memory_leak_detect(self):
        return self._memory_utils_obj.test_memory_leak_detect()
