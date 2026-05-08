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


class MemoryIntegrityTest(BaseTest):
    """
    Test case for RAM Integrity (MEM-004).
    """

    def pre_test(self):
        super().pre_test()
        self.logger.info("Executing pre-test for MemoryIntegrity Test")
        testbed_utils = TestbedUtils(self.user_input.args.config)
        self.test_size_mb = testbed_utils.get_value("memory_integrity_size_mb") or 50

    def do_test(self):
        self.logger.info(f"Running Memory Integrity Test - {self.test_size_mb} MB")

        os_obj = OSBaseAPI(self.platform_obj)
        output, error, exit_status = os_obj.memory.integrity_test(self.test_size_mb)
        
        final_output = output.strip()
        if not final_output and error.strip():
            final_output = error.strip()
            
        self.logger.info(f"Memory Integrity Output:\n{final_output}")

        if exit_status == 0:
            self.result.set_result(True, "Memory Integrity test succeeded")
        else:
            self.logger.error(f"Memory Integrity test failed: {error}")
            self.result.set_result(False, "Memory Integrity test failed")

        return exit_status

if __name__ == "__main__":
    test = MemoryIntegrityTest()
    test.run()
