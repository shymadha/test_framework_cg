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


class StorageRandomRwTest(BaseTest):
    def pre_test(self):
        super().pre_test()
        self.logger.info("Executing pre-test for StorageRandomRw Test")
        testbed_utils = TestbedUtils(self.user_input.args.config)
        self.size_mb = testbed_utils.get_value("storage_test_size_mb") or 100
        self.test_file = testbed_utils.get_value("storage_test_file") or "test_rand.bin"

    def do_test(self):
        self.logger.info(f"Running Storage Random R/W Test - {self.size_mb} MB")

        os_obj = OSBaseAPI(self.platform_obj)
        # Ensure file exists
        os_obj.storage.sequential_write(self.test_file, self.size_mb)
        output, error, exit_status = os_obj.storage.random_rw(self.test_file, self.size_mb)

        self.logger.info(f"Random R/W Output: {output}")

        if exit_status == 0:
            self.result.set_result(True, "Random R/W succeeded")
        else:
            self.logger.error(f"Random R/W failed: {error}")
            self.result.set_result(False, "Random R/W failed")

        return exit_status

if __name__ == "__main__":
    test = StorageRandomRwTest()
    test.run()
