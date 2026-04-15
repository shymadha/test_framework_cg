# framework/tests/gpio/gpio_input_read_test.py

"""
GPIO Input Read Test
--------------------

This test verifies that a specified GPIO pin can be read successfully
on the target platform. It uses the GpioUtilsAPI abstraction to perform
the read operation and reports the result.

Workflow:
1. Reads the GPIO pin number from the testbed configuration.
2. Calls the platform's GPIO utility to read the pin value.
3. Logs output and error messages.
4. Marks the test as PASS if the read succeeds, otherwise FAIL.

Intended use:
- Run as part of the automated test framework.
- Validate GPIO input functionality on BeagleBone or other supported platforms.
"""

import sys, os
from pathlib import Path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Add project root BEFORE any framework imports
current = Path(__file__).resolve()
for parent in current.parents:
    if (parent / "framework").exists():
        sys.path.insert(0, str(parent))
        break

from framework.tests.base_test import BaseTest
from core.testbed_utils import TestbedUtils
from framework.utilities.os_utils.gpio.api_intf_gpio import GpioUtilsAPI

class GpioInputReadTest(BaseTest):
    """Test case for reading a GPIO input pin."""

    def pre_test(self):
        """
        Pre-test setup:
        - Calls the base pre_test routine.
        - Loads the GPIO pin number from the testbed configuration.
        """
        super().pre_test()
        self.logger.info("Executing pre-test for GpioInputReadTest")
        tb = TestbedUtils(self.user_input.args.config)
        self.gpio_pin = tb.get_value("gpio_pin")

    def do_test(self):
        """
        Executes the GPIO input read test:
        - Logs the start of the test.
        - Uses GpioUtilsAPI to read the configured GPIO pin.
        - Sets the test result to PASS if status == 0, otherwise FAIL.
        """
        self.logger.info("Running GPIO Input Read Test")
        gpio_obj = GpioUtilsAPI(self.platform_obj.get_os_type(), self.platform_obj)
        out, err, status = gpio_obj.input_read(self.gpio_pin)

        if status == 0:
            self.result.set_result(True, f"Read value: {out.strip()}")
        else:
            self.result.set_result(False, f"Failed read: {err}")
        return status

if __name__ == "__main__":
    test = GpioInputReadTest()
    test.run()
