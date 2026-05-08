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


class EthernetLinkStatusTest(BaseTest):
    """
    Test case to check the Ethernet link status on the target device.

    This test uses the Ethernet utility functions available via OSBaseAPI
    to determine whether the Ethernet interface reports its link as
    "up" or "down". The test:
      - Executes a link status check command.
      - Evaluates command output and exit status.
      - Marks the test as PASS or FAIL based on link state and output validity.

    Inherits from BaseTest, which provides:
      - Standard logging
      - Test lifecycle (pre_test → do_test → post_test)
      - Storage for test results
      - Access to platform and user input context
    """

    def pre_test(self):
        """
        Run pre-test steps for Ethernet link validation.

        Steps:
          1. Invoke BaseTest.pre_test() for setup.
          2. Log the start of Ethernet link status pre-test activities.

        Raises
        ------
        Exception
            If base initialization encounters errors.
        """
        super().pre_test()
        self.logger.info("Executing pre-test for EthernetLinkStatusTest")

    def do_test(self):
        """
        Execute the Ethernet link status test.

        Steps:
          1. Create an OSBaseAPI wrapper bound to the active platform.
          2. Use ethernet.check_link_status() to query the link state.
          3. Log the result output for visibility.
          4. Determine PASS/FAIL based on:
                - Exit status
                - Output values ("up" or "down")
                - Non-empty responses

        Returns
        -------
        int
            Exit status from the Ethernet link status command.

        Raises
        ------
        Exception
            If unexpected errors occur during command execution.
        """
        self.logger.info("Running Ethernet Link Status Test")

        ethernet_obj = OSBaseAPI(self.platform_obj)
        output, error, exit_status = ethernet_obj.ethernet.check_link_status()

        self.logger.info(f"Link Status Output: {output}")

        # Success scenarios
        if exit_status == 0 and output.lower() == "up":
            self.result.set_result(True, "Ethernet link is up")
        elif exit_status == 0 and output.lower() == "down":
            self.result.set_result(False, "Ethernet link is down")

        # Command succeeded but output was empty
        elif exit_status == 0 and not output.strip():
            self.result.set_result(False, "Link status output was empty")
            self.logger.error(
                "No link status information returned despite successful command execution"
            )

        # Full failure scenario
        else:
            self.result.set_result(False, f"Link status check failed: {error}")
            self.logger.error(f"Link status command failed with error: {error}")

        return exit_status


if __name__ == "__main__":
    """
    Entry point to execute EthernetLinkStatusTest as a standalone test.

    Instantiates the test class and begins the standard BaseTest/TestEngine
    workflow.
    """
    test = EthernetLinkStatusTest()
    test.run()