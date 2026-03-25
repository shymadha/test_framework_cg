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
    Test case for checking the Ethernet link status.
    Uses OSBaseAPI to run platform-specific commands (Linux or Windows).
    """

    def pre_test(self):
        """
        Perform pre-test setup for Ethernet link status.

        Responsibilities:
        - Call the BaseTest pre_test() method.
        - Log that the pre-test phase has started.
        """
        super().pre_test()
        self.logger.info("Executing pre-test for EthernetLinkStatusTest")

    def do_test(self):
        """
        Execute the Ethernet link status test.

        Steps:
        - Instantiate OSBaseAPI with the current platform object.
        - Call ethernet.check_link_status() to retrieve link status.
        - Log the command output.
        - Evaluate results:
            * PASS if exit_status == 0 and output is "up".
            * FAIL if exit_status == 0 and output is "down".
            * FAIL if exit_status == 0 but output is empty.
            * FAIL if exit_status != 0 (command error).
        - Set the test result accordingly.

        Returns:
            int: exit_status from the command execution
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

        # Failure scenarios
        elif exit_status == 0 and not output.strip():
            self.result.set_result(False, "Link status output was empty")
            self.logger.error("No link status information returned despite successful command execution")
        else:
            self.result.set_result(False, f"Link status check failed: {error}")
            self.logger.error(f"Link status command failed with error: {error}")

        return exit_status


if __name__ == "__main__":
    """
    Entry point for standalone execution of the test.
    Creates an instance of EthernetLinkStatusTest and runs it.
    """
    test = EthernetLinkStatusTest()
    test.run()
