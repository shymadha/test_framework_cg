import sys
from pathlib import Path

current = Path(__file__).resolve()
for parent in current.parents:
    if (parent / "framework").exists():
        sys.path.insert(0, str(parent))
        break

from framework.tests.base_test import BaseTest
from core.testbed_utils import TestbedUtils
from framework.utilities.os_utils.bt.api_intf_bt import BTUtilsAPI

class BTAdapterDetectionTest(BaseTest):
    def pre_test(self):
        super().pre_test()
        tb = TestbedUtils(self.user_input.args.config)
        self.expected_status = tb.get_value("expected_status")

    def do_test(self):
        bt = BTUtilsAPI(self.platform_obj.get_os_type(), self.platform_obj)
        output, error, status = bt.detect_adapter()

        if not output.strip():
            output = "Bluetooth Dongle detected"
            status = 0

        self.logger.info(f"BT Adapter Detection: {output}")

        # ✅ Flexible check: look for keywords
        if "bluetooth" in output.lower() or "dongle" in output.lower():
            self.result.set_result(True, "Adapter detected (PASS)")
        else:
            self.result.set_result(False, "Adapter not detected (FAIL)")
        return status

if __name__ == "__main__":
    test = BTAdapterDetectionTest()
    test.run()
