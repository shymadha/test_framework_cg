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

class EthernetDeviceDetectionTest(BaseTest):
    def pre_test(self):
        super().pre_test()
        self.logger.info("Executing pre-test for EthernetDeviceDetectionTest")

    def do_test(self):
        self.logger.info("Running Ethernet Device Detection Test")
        eth_obj = EthernetUtilsAPI(self.platform_obj.get_os_type(), self.platform_obj)
        output, error, exit_status = eth_obj.detect_device()

        self.logger.info(f"Device Detection Output: {output}")

        # Success scenario
        if exit_status == 0 and output.strip():
            self.result.set_result(True, "Ethernet device detected successfully")
        # Failure scenarios
        elif exit_status == 0 and not output.strip():
            self.result.set_result(False, "No Ethernet device found in output")
            self.logger.error("Output was empty despite successful command execution")
        else:
            self.result.set_result(False, f"Ethernet device detection failed: {error}")
            self.logger.error(f"Detection command failed with error: {error}")

        return exit_status

if __name__ == "__main__":
    test = EthernetDeviceDetectionTest()
    test.run()
