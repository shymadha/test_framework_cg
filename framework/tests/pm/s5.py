import sys
import os
from pathlib import Path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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


class s5Test(BaseTest):
    """
    Test case to validate system s5 functionality on the target platform.

    This test:
      - Reads 's5' and 'password' parameters from the testbed configuration.
      - Uses the OSBaseAPI to call pm.s5(), which triggers a system s5.
      - Logs output, errors, and exit status for debugging.
      - Marks the test as PASS if the s5 command executed successfully.

    Inherits from BaseTest, which provides:
      - Logging utilities
      - Access to platform and user input parser
      - Test lifecycle (pre_test → do_test → post_test)
      - Result handling via TestResult
    """

    def pre_test(self):
        """
        Perform pre-test setup before executing the s5 test.

        Steps:
          1. Call BaseTest.pre_test() to initialize common components.
          2. Use TestbedUtils to retrieve:
               - 's5' parameter from testbed config.
               - 'password' needed for privileged s5 execution.

        Raises
        ------
        Exception
            If configuration loading or key retrieval fails.
        """
        super().pre_test()
        testbed_utils = TestbedUtils(self.user_input.args.config)
        self.min_cores = testbed_utils.get_value("s5")
        self.password = testbed_utils.get_value("password")

    def do_test(self):
        """
        Execute the system s5 test.

        Steps:
          1. Create an OSBaseAPI instance bound to the current platform.
          2. Call pm.s5() to trigger s5 flow.
          3. Log the result of the operation.
          4. Determines PASS/FAIL based on return type:
               - Tuple (output, error, exit_status): legacy path.
               - String status code: updated pm_win.py path.

        Returns
        -------
        int
            0 if s5 flow succeeded, -1 otherwise.

        Raises
        ------
        Exception
            If the s5 API call fails unexpectedly.
        """
        self.logger.info("Running s5 Test")

        pm_obj = OSBaseAPI(self.platform_obj)
        result = pm_obj.pm.s5()

        self.logger.info(f"Result : {result}")

        # ── Handle tuple return (output, error, exit_status) ─────────────
        if isinstance(result, tuple):
            output, error, exit_status = result

            # Success scenario
            if exit_status == 0:
                self.logger.info("s5 command executed successfully.")
                self.result.set_result(True, "s5 triggered successfully")

            # Command succeeded but no useful result
            elif exit_status == 0 and not output.strip():
                self.logger.error(
                    "s5 output was empty despite successful execution."
                )
                self.result.set_result(False, "s5 output was empty")
                exit_status = -1

            # Complete failure or unexpected error
            else:
                self.logger.error(f"s5 command failed with error: {error}")
                self.result.set_result(False, "s5 command failed")
                exit_status = -1

        # ── Handle string return (after pm_win.py is updated) ────────────
        elif result == "success":
            self.logger.info("s5 and Wake-on-LAN flow completed successfully.")
            self.result.set_result(True, "s5 triggered successfully")
            exit_status = 0

        elif result == "mac_failed":
            self.logger.error(
                "MAC address detection failed — check NIC or getmac output."
            )
            self.result.set_result(False, "MAC address detection failed")
            exit_status = -1

        elif result == "s5_failed":
            self.logger.error(
                "s5 command failed — check SSH privileges."
            )
            self.result.set_result(False, "s5 command failed")
            exit_status = -1

        elif result == "wol_failed":
            self.logger.error(
                "WoL magic packet failed — check BIOS WoL and network."
            )
            self.result.set_result(False, "Wake-on-LAN failed")
            exit_status = -1

        elif result == "exception":
            self.logger.error(
                "Unexpected exception occurred during s5 flow."
            )
            self.result.set_result(False, "Unexpected error in s5 flow")
            exit_status = -1

        else:
            self.logger.error(f"Unexpected result from s5: {result!r}")
            self.result.set_result(False, "Unknown s5 result")
            exit_status = -1

        self.logger.info(f"Exit Status : {exit_status}")
        return exit_status


if __name__ == "__main__":
    """
    Entry point to execute s5Test as a standalone script.

    Creates an instance of s5Test and runs it via BaseTest/TestEngine workflow.
    """
    test = s5Test()
    test.run()