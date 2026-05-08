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


class StorageRepeatedWriteTest(BaseTest):
    def pre_test(self):
        super().pre_test()
        self.logger.info("Executing pre-test for StorageRepeatedWrite Test")
        testbed_utils = TestbedUtils(self.user_input.args.config)
        self.size_mb = testbed_utils.get_value("storage_test_size_mb") or 10
        self.test_file = testbed_utils.get_value("storage_test_file") or "test_rep_write"
        self.cycles = testbed_utils.get_value("storage_test_cycles") or 5

    def do_test(self):
        self.logger.info(f"Running Storage Repeated Write Test - {self.size_mb} MB * {self.cycles} cycles")

        os_obj = OSBaseAPI(self.platform_obj)
        output, error, exit_status = os_obj.storage.repeated_write(self.test_file, self.size_mb, self.cycles)

        self.logger.info(f"Repeated Write Output: {output}")

        if exit_status == 0:
            self.result.set_result(True, "Repeated write succeeded")
        else:
            self.logger.error(f"Repeated write failed: {error}")
            self.result.set_result(False, "Repeated write failed")

        return exit_status

if __name__ == "__main__":
    test = StorageRepeatedWriteTest()
    test.run()
