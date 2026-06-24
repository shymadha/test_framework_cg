import os
import sys
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

current = Path(__file__).resolve()

for parent in current.parents:
    if (parent / "framework").exists():
        sys.path.insert(0, str(parent))
        break

from framework.tests.base_test import BaseTest
from framework.utilities.os_utils.api_intf_os_base import OSBaseAPI


class Mem002Test(BaseTest):
    def pre_test(self):
        super().pre_test()
        self.logger.info("Executing pre-test for Mem002Test")

    def do_test(self):
        self.logger.info("Running MEM-002 RAM R/W Speed Test")
        os_obj = OSBaseAPI(self.platform_obj)
        output, error, exit_status = os_obj.memory.test_ram_rw_speed()
        self.logger.info(f"MEM-002 Output: {output}")

        if exit_status == 0:
            self.result.set_result(True, "Successfully ran MEM-002 test")
        else:
            self.result.set_result(False, f"MEM-002 test failed: {error}")
        return exit_status

if __name__ == "__main__":
    test = Mem002Test()
    test.run()
