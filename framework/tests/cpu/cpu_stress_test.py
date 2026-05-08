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


class CpuStressTest(BaseTest):
    """
    Test case to run and validate a CPU stress test on the target platform.

    This test:
      - Reads timeout (duration) for the stress test from the testbed config.
      - Uses OSBaseAPI to invoke a CPU stress function via OS‑appropriate tools.
      - Logs test output and evaluates success based on the command exit status.

    Inherits from BaseTest, which handles:
      - Logger setup
      - Test lifecycle (pre_test → do_test → post_test)
      - Result recording via TestResult
      - Access to platform and user input configuration
    """

    def pre_test(self):
        """
        Perform pre‑test setup before executing the CPU stress test.

        Steps:
          1. Call BaseTest.pre_test() for test environment initialization.
          2. Load testbed config using TestbedUtils.
          3. Retrieve 'timeout' value, which determines how long the stress
             test will run.
          4. Log relevant pre‑test details.

        Raises
        ------
        Exception
            If configuration loading or value retrieval fails.
        """
        super().pre_test()
        self.logger.info("Executing pre-test for CpuStressTest")

        testbed_utils = TestbedUtils(self.user_input.args.config)
        self.timeout = testbed_utils.get_value("timeout")
        self.logger.info(f"The timeout is {self.timeout}")

    def do_test(self):
        """
        Execute the CPU stress test.

        Steps:
          1. Instantiate OSBaseAPI with the current platform object.
          2. Run the CPU stress procedure via test_cpu_stress(timeout).
          3. Log the output and error message (if any).
          4. Set PASS if exit_status == 0; otherwise set FAIL.

        Returns
        -------
        int
            Exit status returned by the CPU stress command.

        Raises
        ------
        Exception
            If CPU stress execution fails unexpectedly.
        """
        self.logger.info("Running CPU Stress Test")
        cpu_obj = OSBaseAPI(self.platform_obj)

        output, error, exit_status = cpu_obj.cpu.test_cpu_stress(self.timeout)

        self.logger.info(f"Stress Test Output: {output}")

        if exit_status == 0:
            self.result.set_result(True, "Successfully ran CPU stress test")
        else:
            self.result.set_result(False, f"CPU stress test failed: {error}")

        return exit_status


if __name__ == "__main__":
    """
    Entry point for running CpuStressTest standalone.

    Instantiates the test class and triggers the test execution workflow
    provided by BaseTest and TestEngine.
    """
    test = CpuStressTest()
    test.run()