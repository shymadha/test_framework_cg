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

class RestartTest(BaseTest):
    """
    Test case to validate system restart functionality.

    This class extends `BaseTest` and performs a reboot operation on the
    target platform using the OSBaseAPI. It retrieves necessary parameters
    from the testbed configuration, triggers a restart command, logs output,
    and sets the final test result based on the success of the operation.
    """

    def pre_test(self):
        """
        Perform pre-test setup actions.

        This method:
        - Calls the parent class `pre_test()` for standard initialization.
        - Loads the required configuration values (reboot settings and password)
          from the testbed configuration file using `TestbedUtils`.

        Sets:
            self.min_cores (Any): Reboot-related configuration parameter.
            self.password (str): Password used to authenticate the restart request.
        """
        super().pre_test()
        testbed_utils = TestbedUtils(self.user_input.args.config)
        self.min_cores = testbed_utils.get_value("reboot")
        self.password = testbed_utils.get_value("password")
     
    def do_test(self):
        """
        Execute the restart test on the target platform.

        This method:
        - Logs the beginning of the restart operation.
        - Creates an OSBaseAPI object for platform-level power management.
        - Invokes the restart command using the retrieved password.
        - Logs command output, error messages, and exit status.
        - Determines test success if:
            * the exit status is 0, or
            * the output contains the word 'reboot' (case-insensitive).
        - Updates the test result accordingly.

        Returns:
            int: The exit status returned by the restart command.
        """
        self.logger.info("Running Restart Test")
        pm_obj = OSBaseAPI(self.platform_obj)
        output, error, exit_status = pm_obj.pm.restart(self.password)

        self.logger.info(f"Output : {output}")
        self.logger.info(f"Error : {error}")
        self.logger.info(f"Exit Status : {exit_status}")

        if exit_status == 0 or "reboot" in output.lower():
            self.result.set_result(True, "Restart triggered successfully")
        else:
            self.result.set_result(False, "Restart failed")

        return exit_status


if __name__ == "__main__":
    """
    Entry point for standalone execution.

    Creates an instance of RestartTest and runs the complete test sequence
    (setup → execution → teardown) using the framework's test runner.
    """
    test = RestartTest()
    test.run()