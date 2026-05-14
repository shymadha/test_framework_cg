import sys
import os
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

current = Path(__file__).resolve()

for parent in current.parents:
    if (parent / "framework").exists():
        sys.path.insert(0, str(parent))
        break

from framework.tests.base_test import BaseTest
from framework.utilities.os_utils.api_intf_os_base import OSBaseAPI

class Mem005Test(BaseTest):
    def pre_test(self):
        super().pre_test()
        self.logger.info("Executing pre-test for Mem005Test")

    def do_test(self):
        self.logger.info("Running MEM-005 Memory Leak Detect Test")
        os_obj = OSBaseAPI(self.platform_obj)
        output, error, exit_status = os_obj.memory.test_memory_leak_detect()
        self.logger.info(f"MEM-005 Output: {output}")

        if exit_status == 0:
            self.result.set_result(True, "Successfully ran MEM-005 test")
        else:
            self.result.set_result(False, f"MEM-005 test failed: {error}")
        return exit_status

if __name__ == "__main__":
    test = Mem005Test()
    test.run()
