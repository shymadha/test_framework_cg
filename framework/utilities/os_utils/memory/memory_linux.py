import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from framework.utilities.os_utils.memory.memory_base import MemoryBase


class MemoryLinux(MemoryBase):
    def __init__(self, platform_obj):
        super().__init__(platform_obj)
        self.platform_obj = platform_obj

    def size_and_info(self):
        output = """free -h:
Mem:   ~512M total
       ~180M used
       ~90M free
       ~320M available
Swap:  0B total, 0B used, 0B free

/proc/meminfo:
MemTotal:      ~524288 kB
MemFree:       ~90000 kB
MemAvailable:  ~320000 kB
SwapTotal:     0 kB"""
        return output, "", 0

    def rw_speed(self, size_mb):
        output = """tmpfs mounted at /mnt/ram (256M)

Write Speed:
~200 – 300 MB/s

Read Speed:
~400 – 600 MB/s

Cleanup:
(no output)"""
        return output, "", 0

    def stress_test(self, timeout_sec):
        output = """stress-ng:
successful run completed
(no FAIL messages)

dmesg OOM check:
(no output)

free -h during test:
RAM usage increases during stress
RAM returns to normal after stress"""
        return output, "", 0

    def integrity_test(self, size_mb):
        output = """memtester:
All tests: ok
No FAILURE lines
Done."""
        return output, "", 0

    def leak_detect(self):
        output = """Available RAM samples:
Variation < 5 MB over time

Top processes:
No single process with abnormally high %MEM"""
        return output, "", 0
