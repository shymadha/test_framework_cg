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
    def pre_test(self):
        super().pre_test()
        self.logger.info("Executing pre-test for EthernetConnectivityTest")

    def do_test(self):
        self.logger.info("Running Ethernet Connectivity Test")
        ethernet_obj = OSBaseAPI(self.platform_obj)
        output,error,exit_status = ethernet_obj.ethernet.test_connectivity()
        self.logger.info(f"Connectivity Test Output: {output}")

        # Success scenario
        if exit_status == 0 and "google.com" in output.lower():
            self.result.set_result(True, "Network connectivity verified")

        # Failure scenarios
        elif exit_status == 0 and not output.strip():
            self.result.set_result(False, "Connectivity output was empty")
            self.logger.error("No connectivity information returned despite successful command execution")
        else:
            self.result.set_result(False, f"Connectivity test failed: {error}")
            self.logger.error(f"Connectivity command failed with error: {error}")

        return exit_status

if __name__ == "__main__":
    test = EthernetConnectivityTest()
    test.run()
