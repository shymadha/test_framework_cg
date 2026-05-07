import sys
import os
from pathlib import Path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Add project root BEFORE any framework imports
current = Path(__file__).resolve()

for parent in current.parents:
    if (parent / "framework").exists():
        sys.path.insert(0, str(parent))
        break

import argparse
from framework.core.test_engine import TestEngine
from framework.core.user_input_parser import ParseUserInput
from tests.base_test import BaseTest
from core.testbed_utils import TestbedUtils
from framework.utilities.os_utils.api_intf_os_base import OSBaseAPI


class CpuCoreCountTest(BaseTest):
    """
    Test case to validate minimum CPU core count on the target platform.

    This test:
      - Reads expected minimum cores from the testbed JSON file.
      - Uses the OS API layer to query the actual CPU core count.
      - Compares actual vs expected and records a PASS/FAIL result.

    Inherits from BaseTest, which provides:
      - Logging
      - Test result handling
      - Access to platform object
      - Test execution flow control
    """

    def pre_test(self):
        """
        Perform pre-test initialization for CPU core validation.

        Steps:
          1. Call the base class pre_test() to perform framework-level setup.
          2. Log pre-test actions.
          3. Load the testbed configuration via TestbedUtils.
          4. Extract the 'min_cores' value, which defines the required minimum.

        Raises
        ------
        Exception
            If configuration loading or parsing fails.
        """
        super().pre_test()
        self.logger.info("Executing pre-test for CpuCoreCount")

        testbed_utils = TestbedUtils(self.user_input.args.config)

        self.min_cores = testbed_utils.get_value("min_cores")
        print(f"The min_cores is {self.min_cores}")

    def do_test(self):
        """
        Validate detected CPU core count against the configured minimum.

        Steps:
          1. Retrieve CPU information via OSBaseAPI.
          2. Execute the CPU core count query.
          3. Convert output to integer using ParseUserInput helper.
          4. Compare actual core count to expected minimum.
          5. Set PASS/FAIL result accordingly.

        Returns
        -------
        int
            Exit status returned by the underlying OS command.

        Raises
        ------
        Exception
            If command execution or output parsing fails.
        """
        self.logger.info("Running CPU Core Count Test")

        cpu_obj = OSBaseAPI(self.platform_obj)
        output, error, exit_status = cpu_obj.cpu.get_core_count()

        self.logger.info(f"The core count is {output}")

        output = self.user_input.parse_int_output(output)

        if output >= self.min_cores:
            self.result.set_result(True, "Valid core count")
        else:
            self.result.set_result(False, "Invalid core count")

        return exit_status


if __name__ == "__main__":
    """
    Entry point for standalone execution of the CpuCoreCountTest.

    Creates an instance of the test class and invokes the test flow via run().
    """
    test = CpuCoreCountTest()
    test.run()