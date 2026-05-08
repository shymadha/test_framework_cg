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


class EthernetDeviceDetectionTest(BaseTest):
    """
    Test case to detect the presence of Ethernet devices on the target platform.

    This test uses the Ethernet utility interface exposed through OSBaseAPI
    to execute an Ethernet device detection command. The test:
      - Captures stdout, stderr, and exit status from the OS-level detection API
      - Logs all relevant output for debugging
      - Determines PASS/FAIL based on output presence and exit status

    Inherits from BaseTest, which provides:
      - Logging utilities
      - Test result storage via TestResult
      - Access to parsed user input and platform objects
      - Test execution flow (pre_test → do_test → post_test)
    """

    def pre_test(self):
        """
        Perform framework-level and test-specific initialization steps.

        Steps:
          1. Execute BaseTest.pre_test() for common test setup.
          2. Log that EthernetDeviceDetectionTest pre-test setup has begun.

        Raises
        ------
        Exception
            If initialization in the base class fails.
        """
        super().pre_test()
        self.logger.info("Executing pre-test for EthernetDeviceDetectionTest")

    def do_test(self):
        """
        Execute the Ethernet device detection test.

        This method:
          1. Instantiates OSBaseAPI using the active platform object.
          2. Invokes ethernet.detect_device() to query available Ethernet interfaces.
          3. Logs the command output.
          4. Determines test success using:
                - exit_status
                - whether the output is non-empty

        Returns
        -------
        int
            Exit status returned by the Ethernet device detection command.

        Raises
        ------
        Exception
            If device detection execution encounters an unexpected failure.
        """
        self.logger.info("Running Ethernet Device Detection Test")

        ethernet_obj = OSBaseAPI(self.platform_obj)
        output, error, exit_status = ethernet_obj.ethernet.detect_device()

        self.logger.info(f"Device Detection Output: {output}")

        # Success scenario: command succeeded *and* output contains data
        if exit_status == 0 and output.strip():
            self.result.set_result(True, "Ethernet device detected successfully")

        # Command succeeded but returned no usable information
        elif exit_status == 0 and not output.strip():
            self.result.set_result(False, "No Ethernet device found in output")
            self.logger.error("Output was empty despite successful command execution")

        # Command failed entirely
        else:
            self.result.set_result(False, f"Ethernet device detection failed: {error}")
            self.logger.error(f"Detection command failed with error: {error}")

        return exit_status


if __name__ == "__main__":
    """
    Standalone entry point for executing the EthernetDeviceDetectionTest.

    Creates an instance of the test class and triggers the test execution
    workflow defined in BaseTest and TestEngine.
    """
    test = EthernetDeviceDetectionTest()
    test.run()