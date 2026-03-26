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
from framework.tests.base_test import BaseTest
from framework.utilities.os_utils.pm.pm_base import PMBase


class SleepTest(BaseTest):
    """
    Test case to validate system sleep (S3) behavior on the target platform.

    This test:
      - Reads 'sleep_duration' and 'password' parameters from the testbed config.
      - Uses the OS power management API (`pm_obj.pm.s3_sleep`) to trigger S3 sleep.
      - Logs output, errors, and status for debugging and analysis.
      - Marks the test as PASS if sleep was successfully triggered.

    Inherits from BaseTest, which provides:
      - Logging utilities
      - Test lifecycle flow (pre_test → do_test → post_test)
      - Platform and user input access
      - Result handling through TestResult
    """

    def pre_test(self):
        """
        Perform pre‑test initialization before running the sleep test.

        Steps:
          1. Calls BaseTest.pre_test() to initialize platform, user input, and logger.
          2. Loads testbed configuration using TestbedUtils.
          3. Extracts:
               - `sleep_duration`: duration the test expects the system to sleep.
               - `password`: system password required to trigger S3 sleep.
        
        Raises
        ------
        Exception
            If the configuration file is missing parameters or fails to load.
        """
        super().pre_test()
        testbed_utils = TestbedUtils(self.user_input.args.config)
        self.sleep_duration = testbed_utils.get_value("sleep_duration")
        self.password = testbed_utils.get_value("password")

    def do_test(self):
        """
        Execute the S3 sleep test.

        Steps:
          1. Creates an OSBaseAPI instance tied to the platform object.
          2. Calls pm.s3_sleep(password) to initiate S3 sleep.
          3. Logs stdout, stderr, and exit status for transparency.
          4. Sets result PASS if exit_status == 0; otherwise FAIL.

        Returns
        -------
        int
            Exit status returned by the S3 sleep command.

        Raises
        ------
        Exception
            If pm.s3_sleep fails unexpectedly or returns invalid output.
        """
        self.logger.info("Running Sleep Test")

        pm_obj = OSBaseAPI(self.platform_obj)
        output, error, exit_status = pm_obj.pm.s3_sleep(self.password)

        self.logger.info(f"Output : {output}")
        self.logger.info(f"Error : {error}")
        self.logger.info(f"Exit Status : {exit_status}")

        if exit_status == 0:
            self.result.set_result(True, "Sleep triggered successfully")
        else:
            self.result.set_result(False, "Sleep failed")

        return exit_status


if __name__ == "__main__":
    """
    Entry point to execute the SleepTest as a standalone script.

    Instantiates SleepTest and runs it using the BaseTest/TestEngine workflow.
    """
    test = SleepTest()
    test.run()