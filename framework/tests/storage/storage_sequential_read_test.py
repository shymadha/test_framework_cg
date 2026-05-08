import sys
import os
from pathlib import Path

current = Path(__file__).resolve()
for parent in current.parents:
    if (parent / "framework").exists():
        sys.path.insert(0, str(parent))
        break

from framework.tests.base_test import BaseTest
from framework.core.testbed_utils import TestbedUtils
from framework.utilities.os_utils.api_intf_os_base import OSBaseAPI


class StorageSequentialReadTest(BaseTest):
    def pre_test(self):
        super().pre_test()
        self.logger.info("Executing pre-test for StorageSequentialRead Test")
        testbed_utils = TestbedUtils(self.user_input.args.config)
        self.test_file = testbed_utils.get_value("storage_test_file") or "test_seq_write.bin"

    def do_test(self):
        self.logger.info(f"Running Storage Sequential Read Test on {self.test_file}")

        os_obj = OSBaseAPI(self.platform_obj)
        # Ensure file exists before reading
        os_obj.storage.sequential_write(self.test_file, 10) # create 10MB dummy
        output, error, exit_status = os_obj.storage.sequential_read(self.test_file)

        self.logger.info(f"Sequential Read Output: {output}")

        if exit_status == 0:
            self.result.set_result(True, "Sequential read succeeded")
        else:
            self.logger.error(f"Sequential read failed: {error}")
            self.result.set_result(False, "Sequential read failed")

        return exit_status

if __name__ == "__main__":
    test = StorageSequentialReadTest()
    test.run()
