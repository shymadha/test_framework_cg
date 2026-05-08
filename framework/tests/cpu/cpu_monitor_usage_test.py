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

from framework.tests.base_test import BaseTest
from framework.utilities.os_utils.api_intf_os_base import OSBaseAPI


class CpuMonitorUsageTest(BaseTest):
    """
    Test case to monitor and validate CPU usage on the target platform.

    This test uses the OSBaseAPI abstraction to retrieve CPU usage
    information from the underlying operating system. The test:
      - Executes a CPU usage monitoring command
      - Captures and logs the output
      - Marks the result as PASS or FAIL based on exit status

    Inherits from BaseTest, which provides:
      - Logging support
      - Test result management
      - Access to platform and user input parser
      - Full test execution lifecycle
    """

    def pre_test(self):
        """
        Perform pre-test setup actions before executing CPU usage monitoring.

        Steps:
          1. Call BaseTest.pre_test() to initialize common components.
          2. Log the start of CpuMonitorUsageTest initialization.

        Raises
        ------
        Exception
            If any part of the initialization process fails.
        """
        super().pre_test()
        self.logger.info("Executing pre-test for CpuMonitorUsageTest")

    def do_test(self):
        """
        Execute the CPU usage monitoring test.

        Steps:
          1. Create an OSBaseAPI instance wired to the active platform.
          2. Invoke the CPU usage monitoring API.
          3. Log output, errors, and status.
          4. Mark test result PASS if exit_status == 0, otherwise FAIL.

        Returns
        -------
        int
            Exit status returned by the underlying OS command.
            A value of 0 means CPU usage retrieval was successful.

        Raises
        ------
        Exception
            If command execution or CPU monitoring API fails unexpectedly.
        """
        self.logger.info("Running CPU Monitor Usage Test")

        cpu_obj = OSBaseAPI(self.platform_obj)
        output, error, exit_status = cpu_obj.cpu.monitor_cpu_usage()

        self.logger.info(f"Monitor Usage Output: {output}")

        if exit_status == 0:
            self.result.set_result(True, "Successfully retrieved CPU usage")
        else:
            self.result.set_result(False, f"CPU usage test failed: {error}")

        return exit_status


if __name__ == "__main__":
    """
    Entry point for standalone execution of the CpuMonitorUsageTest.

    Creates an instance of the test class and runs it using the test engine
    lifecycle defined in BaseTest.
    """
    test = CpuMonitorUsageTest()
    test.run()