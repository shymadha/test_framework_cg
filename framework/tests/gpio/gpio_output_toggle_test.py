import sys, os
from pathlib import Path
import argparse
import webbrowser
from flask import Flask, jsonify

# Ensure project root is on sys.path
current = Path(__file__).resolve()
for parent in current.parents:
    if (parent / "framework").exists():
        sys.path.insert(0, str(parent))
        break

from framework.tests.base_test import BaseTest
from core.testbed_utils import TestbedUtils
from framework.utilities.os_utils.gpio.api_intf_gpio import GpioUtilsAPI


class GpioOutputToggleTest(BaseTest):
    """
    Test case to validate GPIO output toggling on the target platform.

    Supports both CLI and UI:
      - CLI: requires --config to load pin from testbed.json
      - UI: starts a Flask server and opens browser to show results
    """

    def pre_test(self):
        super().pre_test()
        self.logger.info("Executing pre-test for GpioOutputToggleTest")
        if getattr(self.user_input.args, "config", None):
            tb = TestbedUtils(self.user_input.args.config)
            self.gpio_pin = tb.get_value("gpio_pin")
        else:
            self.gpio_pin = "17"  # default pin for UI mode

    def do_test(self):
        self.logger.info("Running GPIO Output Toggle Test")
        gpio_obj = GpioUtilsAPI(self.platform_obj.get_os_type(), self.platform_obj)
        out, err, status = gpio_obj.output_toggle(self.gpio_pin)

        if status == 0:
            self.result.set_result(True, f"Toggled pin {self.gpio_pin}")
        else:
            self.result.set_result(False, f"Failed toggle: {err}")
        return status


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", help="Path to config file", required=False)
    parser.add_argument("--ui", action="store_true", help="Run in UI mode")
    args, unknown = parser.parse_known_args()

    if args.ui:
        # Inject default config if none provided
        if not args.config:
            args.config = "userinput/testbed.json"
        sys.argv = [sys.argv[0], "--config", args.config] + unknown

        # 🔹 Start Flask server
        app = Flask(__name__)

        @app.route("/run/gpio_output_toggle")
        def run_gpio_output_toggle():
            test = GpioOutputToggleTest()
            test.run()
            verdict = "PASS" if test.result.passed else "FAIL"
            return jsonify({
                "test": test.result.name,
                "verdict": verdict,
                "message": test.result.message
            })

        # 🔹 Open browser automatically
        webbrowser.open("http://127.0.0.1:5000/run/gpio_output_toggle")

        app.run(host="0.0.0.0", port=5000)

    else:
        # Normal CLI mode
        if not args.config:
            print("Error: --config is required in CLI mode")
            sys.exit(1)
        sys.argv = [sys.argv[0], "--config", args.config] + unknown
        test = GpioOutputToggleTest()
        test.run()
        verdict = "PASS" if test.result.passed else "FAIL"
        print(f"{test.result.name}: {verdict} - {test.result.message}")
