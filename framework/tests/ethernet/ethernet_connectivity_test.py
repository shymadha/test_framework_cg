import sys
import os
from pathlib import Path

# Ensure project root is on sys.path (same as CPU tests)
current = Path(__file__).resolve()
for parent in current.parents:
    if (parent / "framework").exists():
        sys.path.insert(0, str(parent))
        break

from framework.tests.base_test import BaseTest
from framework.utilities.os_utils.ethernet.api_intf_ethernet import EthernetUtilsAPI
from framework.utilities.os_utils.api_intf_os_base import OSBaseAPI


class EthernetConnectivityTest(BaseTest):
    """
    Test case to validate Ethernet network connectivity on the target platform.

    This test uses OSBaseAPI to interact with the Ethernet utility layer
    (EthernetUtilsAPI) and performs a connectivity check by reaching out
    to a known external host. The output, error code, and overall status
    determine whether the device has functioning network connectivity.

    Inherits from BaseTest, which provides:
      - Logging setup
      - Platform and user input parsing
      - Test lifecycle orchestration (pre_test → do_test → post_test)
      - TestResult handling
    """

    def pre_test(self):
        """
        Perform pre-test initialization before executing the connectivity test.

        Steps:
          1. Execute BaseTest.pre_test() to initialize common test state.
          2. Log the start of Ethernet connectivity pre-test setup.

        Raises
        ------
        Exception
            If any initialization logic in BaseTest fails.
        """
        super().pre_test()
        self.logger.info("Executing pre-test for EthernetConnectivityTest")

    def do_test(self):
        """
        Execute the Ethernet connectivity test.

        Steps:
          1. Create an OSBaseAPI instance bound to the active platform.
          2. Invoke ethernet.test_connectivity().
          3. Log command output.
          4. Determine PASS/FAIL based on:
                - exit_status
                - presence of expected host in output (e.g., 'google.com')
                - non-empty result

        Returns
        -------
        int
            Exit status returned by the connectivity command.

        Raises
        ------
        Exception
            If OS-level API calls fail unexpectedly.
        """
        self.logger.info("Running Ethernet Connectivity Test")

        ethernet_obj = OSBaseAPI(self.platform_obj)
        output, error, exit_status = ethernet_obj.ethernet.test_connectivity()

        self.logger.info(f"Connectivity Test Output: {output}")

        # Success scenario
        if exit_status == 0 and "google.com" in output.lower():
            self.result.set_result(True, "Network connectivity verified")

        # Command succeeded but no useful result
        elif exit_status == 0 and not output.strip():
            self.result.set_result(False, "Connectivity output was empty")
            self.logger.error("No connectivity information returned despite successful command execution")

        # Complete failure or unexpected error
        else:
            self.result.set_result(False, f"Connectivity test failed: {error}")
            self.logger.error(f"Connectivity command failed with error: {error}")

        return exit_status


if __name__ == "__main__":
    """
    Entry point for executing EthernetConnectivityTest as a standalone script.

    Instantiates the test and runs it through the BaseTest/TestEngine workflow.
    """
    test = EthernetConnectivityTest()
    test.run()