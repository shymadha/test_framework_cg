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


class ShutdownTest(BaseTest):
    """
    Test case to validate system shutdown functionality on the target platform.

    This test:
      - Reads 'shutdown' and 'password' parameters from the testbed configuration.
      - Uses the OSBaseAPI to call pm.shutdown(), which triggers a system shutdown.
      - Logs output, errors, and exit status for debugging.
      - Marks the test as PASS if the shutdown command executed successfully.

    Inherits from BaseTest, which provides:
      - Logging utilities
      - Access to platform and user input parser
      - Test lifecycle (pre_test → do_test → post_test)
      - Result handling via TestResult
    """

    def pre_test(self):
        """
        Perform pre-test setup before executing the shutdown test.

        Steps:
          1. Call BaseTest.pre_test() to initialize common components.
          2. Use TestbedUtils to retrieve:
               - 'shutdown' parameter (if used by downstream logic)
               - 'password' needed for privileged shutdown execution

        Raises
        ------
        Exception
            If configuration loading or key retrieval fails.
        """
        super().pre_test()
        testbed_utils = TestbedUtils(self.user_input.args.config)

        # Although variable name says 'min_cores', here it corresponds to shutdown config
        self.min_cores = testbed_utils.get_value("shutdown")
        self.password = testbed_utils.get_value("password")

    def do_test(self):
        """
        Execute the system shutdown test.

        Steps:
          1. Create an OSBaseAPI instance bound to the current platform.
          2. Call pm.shutdown() to attempt system shutdown.
          3. Log stdout, stderr, and exit status.
          4. Mark the test as PASS if exit_status == 0; else FAIL.

        Returns
        -------
        int
            Exit status of the shutdown operation. Zero indicates success.

        Raises
        ------
        Exception
            If the shutdown API call fails unexpectedly.
        """
        self.logger.info("Running Shutdown Test")

        pm_obj = OSBaseAPI(self.platform_obj)
        output, error, exit_status = pm_obj.pm.shutdown()

        self.logger.info(f"Output : {output}")
        self.logger.info(f"Error : {error}")
        self.logger.info(f"Exit Status : {exit_status}")

        if exit_status == 0:
            self.result.set_result(True, "Shutdown triggered successfully")
        else:
            self.result.set_result(False, "Shutdown failed")

        return exit_status


if __name__ == "__main__":
    """
    Entry point to execute ShutdownTest as a standalone script.

    Creates an instance of ShutdownTest and runs it via BaseTest/TestEngine workflow.
    """
    test = ShutdownTest()
    test.run()