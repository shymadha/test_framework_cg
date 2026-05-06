# # import sys
# # import os

# # sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# # from framework.utilities.os_utils.gpio.gpio_base import GPIOBase

# # class GPIOWindows(GPIOBase):
# #     """
# #     Windows-specific GPIO operations using gpiozero/pyserial/USB relay.
# #     """

# #     def __init__(self, platform_obj):
# #         self.platform_obj = platform_obj

# #     def output_toggle(self, pin, value):
# #         # Normalize value to 0/1
# #         val = 1 if int(value) else 0
# #         cmd = f"usbrelay RELAY{pin}_{val}"
# #         return self.platform_obj.exec_cmd(cmd, "local")

# #     def input_read(self, pin):
# #         cmd = f"usbrelay_read RELAY{pin}"
# #         return self.platform_obj.exec_cmd(cmd, "local")

# #     def led_blink(self, led_name="led0"):
# #         cmd_on = f"usbrelay RELAY1_1"
# #         cmd_off = f"usbrelay RELAY1_0"
# #         out1, err1, st1 = self.platform_obj.exec_cmd(cmd_on, "local")
# #         out2, err2, st2 = self.platform_obj.exec_cmd(cmd_off, "local")
# #         return out1 + out2, err1 + err2, max(st1, st2)

# #     def interrupt_detect(self, pin):
# #         cmd = f"gpiod_event_wait {pin}"
# #         return self.platform_obj.exec_cmd(cmd, "local")

# # framework/utilities/os_utils/gpio/gpio_win.py
# class GPIOWindows:
#     def __init__(self, platform_obj):
#         self.platform_obj = platform_obj

#     def toggle_output(self, pin):
#         return self.platform_obj.exec_cmd("usb-relay toggle", "ssh")

#     def read_input(self, pin):
#         return self.platform_obj.exec_cmd("usb-relay read", "ssh")

#     def blink_led(self, led_name):
#         return self.platform_obj.exec_cmd("usb-relay blink", "ssh")

#     def detect_interrupt(self, pin):
#         return self.platform_obj.exec_cmd("gpiod event wait", "ssh")

# framework/utilities/os_utils/gpio/gpio_win.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from framework.utilities.os_utils.gpio.gpio_base import GPIOBase

class GPIOWindows(GPIOBase):
    """
    Windows-specific implementation of GPIO operations using usb-relay/gpiod.
    """

    def __init__(self, platform_obj):
        super().__init__(platform_obj)

    def output_toggle(self, pin, value=1):
        try:
            return self.platform_obj.exec_cmd("usb-relay toggle", "ssh")
        except Exception as e:
            return "", str(e), -1

    def input_read(self, pin):
        try:
            return self.platform_obj.exec_cmd("usb-relay read", "ssh")
        except Exception as e:
            return "", str(e), -1

    def led_blink(self, led_name="led0"):
        try:
            return self.platform_obj.exec_cmd("usb-relay blink", "ssh")
        except Exception as e:
            return "", str(e), -1

    def interrupt_detect(self, pin):
        try:
            return self.platform_obj.exec_cmd("gpiod event wait", "ssh")
        except Exception as e:
            return "", str(e), -1
