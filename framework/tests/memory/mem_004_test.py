import sys
import os
from pathlib import Path

# Ensure framework path is included
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

current = Path(__file__).resolve()
for parent in current.parents:
    if (parent / "framework").exists():
        sys.path.insert(0, str(parent))
        break

from framework.tests.base_test import BaseTest
from framework.utilities.os_utils.memory.api_intf_memory import MemoryUtilsAPI  

class Mem004Test(BaseTest):
    def pre_test(self):
        super().pre_test()
        self.logger.info("Executing pre-test for Mem004Test")

    def do_test(self):
        self.logger.info("Running MEM-004 RAM Integrity Test")
        # ✅ FIXED: use method instead of missing attribute
        os_name = self.platform_obj.get_os_type()   # or get_os_name()
        mem_obj = MemoryUtilsAPI(os_name, self.platform_obj)
        output, error, exit_status = mem_obj.test_ram_integrity()
        self.logger.info(f"MEM-004 Output: {output}")

        if exit_status == 0:
            self.result.set_result(True, "Successfully ran MEM-004 test")
        else:
            self.result.set_result(False, f"MEM-004 test failed: {error}")
        return exit_status

if __name__ == "__main__":
    test = Mem004Test()
    test.run()

