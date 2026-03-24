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

class EthernetLinkStatusTest(BaseTest):
    def pre_test(self):
        super().pre_test()
        self.logger.info("Executing pre-test for EthernetLinkStatusTest")

    def do_test(self):
        self.logger.info("Running Ethernet Link Status Test")
        eth_obj = EthernetUtilsAPI(self.platform_obj.get_os_type(), self.platform_obj)
        output, error, exit_status = eth_obj.check_link_status()

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
    test = EthernetLinkStatusTest()
    test.run()
