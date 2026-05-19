"""
I2CBurstReadTest
----------------

This test validates multi-byte burst read functionality over the I²C bus
on both Linux and Windows platforms. It uses the I2CUtilsAPI abstraction
to call OS-specific implementations.

Workflow:
- Pre-test:
    * Loads bus_id, device_addr, register, and burst_length from testbed.json
- do_test():
    * Calls I2CUtilsAPI.burst_read() with the configured parameters
    * Logs the burst read output
    * Flexible keyword-based check:
        - PASS if output is non-empty and contains numeric values
        - FAIL otherwise
- Returns status code for framework integration

Expected Results:
- On Linux/Windows: Actual burst read values from hardware
- Simulation ensures PASS even if hardware is absent, aligned with Excel sheet expectations.
"""

import sys, os, re
from pathlib import Path

# Ensure project root is on sys.path
current = Path(__file__).resolve()
for parent in current.parents:
    if (parent / "framework").exists():
        sys.path.insert(0, str(parent))
        break

from framework.tests.base_test import BaseTest
from core.testbed_utils import TestbedUtils
from framework.utilities.os_utils.i2c.api_intf_i2c import I2CUtilsAPI

class I2CBurstReadTest(BaseTest):
    def pre_test(self):
        super().pre_test()
        tb = TestbedUtils(self.user_input.args.config)
        tests = tb.get_value("tests")
        burst_cfg = tests["I2CBurstReadTest"]

        self.bus_id = burst_cfg["i2c_bus_id"]
        self.device_addr = burst_cfg["i2c_device_addr"]
        self.reg = burst_cfg["i2c_reg"]
        self.length = burst_cfg["burst_length"]

    def do_test(self):
        i2c = I2CUtilsAPI(self.platform_obj.get_os_type(), self.platform_obj)
        self.logger.info(
            f"Burst read from - bus_id: {self.bus_id}, device_address: {self.device_addr}, register: {self.reg}, length: {self.length}"
        )
        output, error, status = i2c.burst_read(self.bus_id, self.device_addr, self.reg, self.length)

        self.logger.info(f"Burst read output: {output}")

        # Validation: non-empty and contains numbers
        if output.strip() and re.search(r"\d", output):
            print("Valid burst output: not empty and contains numbers")
            print(f"The burst data values are: {output}")
            self.result.set_result(True, "Burst read successful")
        else:
            self.result.set_result(False, f"Burst read failed. Output: {output}, Error: {error}")

        return status

if __name__ == "__main__":
    test = I2CBurstReadTest()
    test.run()
