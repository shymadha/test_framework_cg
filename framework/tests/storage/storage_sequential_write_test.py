import sys
import os
from pathlib import Path

# Add project root BEFORE any framework imports
current = Path(__file__).resolve()
for parent in current.parents:
    if (parent / "framework").exists():
        sys.path.insert(0, str(parent))
        break

from framework.tests.base_test import BaseTest
from framework.core.testbed_utils import TestbedUtils
from framework.utilities.os_utils.api_intf_os_base import OSBaseAPI


class StorageSequentialWriteTest(BaseTest):
    """
    Test case to measure Sequential Write Speed (STG-001).
    """

    def pre_test(self):
        super().pre_test()
        self.logger.info("Executing pre-test for StorageSequentialWrite Test")
        testbed_utils = TestbedUtils(self.user_input.args.config)
        self.size_mb = testbed_utils.get_value("storage_test_size_mb") or 100
        self.test_file = testbed_utils.get_value("storage_test_file") or "test_seq_write.bin"

    def do_test(self):
        self.logger.info(f"Running Storage Sequential Write Test - {self.size_mb} MB")

        os_obj = OSBaseAPI(self.platform_obj)
        output, error, exit_status = os_obj.storage.sequential_write(self.test_file, self.size_mb)
        
        # In Linux, 'dd' command outputs its result to stderr
        # In Windows, we might have added an explicit output message
        final_output = output.strip()
        if not final_output and error.strip():
            final_output = error.strip()
            
        self.logger.info(f"Sequential Write Output:\n{final_output}")

        if exit_status == 0:
            self.result.set_result(True, "Sequential write succeeded")
        else:
            self.logger.error(f"Sequential write failed: {error}")
            self.result.set_result(False, "Sequential write failed")

        return exit_status

if __name__ == "__main__":
    test = StorageSequentialWriteTest()
    test.run()
