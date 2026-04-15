# framework/tests/gpio/gpio_led_blink_test.py

"""
GPIO LED Blink Test
-------------------

This test verifies that a specified LED device on the target platform
can be blinked successfully. It uses the GpioUtilsAPI abstraction to
trigger the blink operation and reports the result.

Workflow:
1. Reads the LED name from the testbed configuration.
2. Calls the platform's GPIO utility to blink the LED.
3. Logs output and error messages.
4. Marks the test as PASS if the blink succeeds, otherwise FAIL.

Intended use:
- Run as part of the automated test framework.
- Validate LED control functionality on BeagleBone or other supported platforms.
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

class GpioLedBlinkTest(BaseTest):
    """Test case for blinking a GPIO-controlled LED."""

    def pre_test(self):
        """
        Pre-test setup:
        - Calls the base pre_test routine.
        - Loads the LED name from the testbed configuration.
        """
        super().pre_test()
        self.logger.info("Executing pre-test for GpioLedBlinkTest")
        tb = TestbedUtils(self.user_input.args.config)
        self.led_name = tb.get_value("led_name")

    def do_test(self):
        """
        Executes the GPIO LED blink test:
        - Logs the start of the test.
        - Uses GpioUtilsAPI to blink the configured LED.
        - Sets the test result to PASS if status == 0, otherwise FAIL.
        """
        self.logger.info("Running GPIO LED Blink Test")
        gpio_obj = GpioUtilsAPI(self.platform_obj.get_os_type(), self.platform_obj)
        out, err, status = gpio_obj.led_blink(self.led_name)

        if status == 0:
            self.result.set_result(True, f"Blink triggered on {self.led_name}")
        else:
            self.result.set_result(False, f"Failed blink: {err}")
        return status

if __name__ == "__main__":
    test = GpioLedBlinkTest()
    test.run()
