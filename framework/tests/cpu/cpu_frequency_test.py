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


class CpuFrequencyTest(BaseTest):
    """
    Test case for validating CPU frequency retrieval on the target platform.

    This test interacts with the OS API abstraction layer to query
    CPU frequency information provided by the underlying platform.

    The test:
      - Executes a CPU frequency query via OSBaseAPI.
      - Logs the retrieved value.
      - Sets PASS/FAIL based on the command exit code.

    This class inherits from BaseTest, which provides:
      - Common logging utilities
      - Result handling via TestResult
      - Access to platform and user input objects
      - The test lifecycle (pre_test → do_test → post_test)
    """

    def pre_test(self):
        """
        Execute pre-test initialization tasks.

        Steps:
          1. Call the base-class pre_test() to initialize common components.
          2. Log that the CPU frequency pre-test setup has begun.

        Raises
        ------
        Exception
            If any unexpected initialization error occurs.
        """
        super().pre_test()
        self.logger.info("Executing pre-test for CpuFrequencyTest")

    def do_test(self):
        """
        Run the CPU frequency retrieval test.

        Steps:
          1. Initialize OSBaseAPI with the active platform object.
          2. Invoke CPU frequency check via cpu_obj.cpu.check_cpu_frequency().
          3. Log the retrieved output.
          4. Mark the result as PASS if exit_status == 0, else FAIL.

        Returns
        -------
        int
            Exit status returned by the OS command. Zero indicates success.

        Raises
        ------
        Exception
            If the underlying OS command or API layer produces an error.
        """
        self.logger.info("Running CPU Frequency Test")
        cpu_obj = OSBaseAPI(self.platform_obj)

        output, error, exit_status = cpu_obj.cpu.check_cpu_frequency()

        self.logger.info(f"Frequency Test Output: {output}")

        if exit_status == 0:
            self.result.set_result(True, "Successfully retrieved CPU frequency")
        else:
            self.result.set_result(
                False,
                f"CPU frequency scaling test failed: {error}"
            )

        return exit_status


if __name__ == "__main__":
    """
    Entry point for standalone execution of the CpuFrequencyTest.

    Creates a test instance and executes it using the TestEngine-managed
    lifecycle defined in BaseTest.
    """
    test = CpuFrequencyTest()
    test.run()