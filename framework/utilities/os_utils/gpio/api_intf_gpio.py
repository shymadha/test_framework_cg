# # # api_intf_gpio.py
# # import sys
# # import os

# # sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# # from framework.utilities.os_utils.gpio.gpio_linux import GPIOLinux
# # from framework.utilities.os_utils.gpio.gpio_win import GPIOWindows

# # class GPIOUtilsAPI:
# #     """
# #     Unified API wrapper for GPIO utilities across operating systems.

# #     Provides uniform methods for:
# #       - Output toggle
# #       - Input read
# #       - LED blink (health check)
# #       - Interrupt/edge detection
# #     """

# #     def __init__(self, os_name, platform_obj):
# #         self.platform_obj = platform_obj
# #         self.os_name = os_name

# #         if self.os_name.lower() == "windows":
# #             self.__gpio_obj = GPIOWindows(self.platform_obj)
# #         elif self.os_name.lower() == "linux":
# #             self.__gpio_obj = GPIOLinux(self.platform_obj)
# #         else:
# #             raise ValueError(f"Unsupported OS: {self.os_name}")

# #     def output_toggle(self, pin, value):
# #         return self.__gpio_obj.output_toggle(pin, value)

# #     def input_read(self, pin):
# #         return self.__gpio_obj.input_read(pin)

# #     def led_blink(self, led_name="led0"):
# #         return self.__gpio_obj.led_blink(led_name)

# #     def interrupt_detect(self, pin):
# #         return self.__gpio_obj.interrupt_detect(pin)

# # framework/utilities/os_utils/api_intf_gpio.py
# import sys, os
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# from framework.utilities.os_utils.gpio.gpio_linux import GPIOLinux
# from framework.utilities.os_utils.gpio.gpio_win import GPIOWindows

# class GpioUtilsAPI:
#     """
#     Unified API wrapper for GPIO operations across Linux and Windows.
#     """

#     def __init__(self, os_name, platform_obj):
#         self.platform_obj = platform_obj
#         self.os_name = os_name.lower()

#         if self.os_name == "linux":
#             self.__gpio_obj = GPIOLinux(self.platform_obj)
#         elif self.os_name == "windows":
#             self.__gpio_obj = GPIOWindows(self.platform_obj)
#         else:
#             raise ValueError(f"Unsupported OS: {self.os_name}")

#     def toggle_output(self, pin):
#         return self.__gpio_obj.toggle_output(pin)

#     def read_input(self, pin):
#         return self.__gpio_obj.read_input(pin)

#     def blink_led(self, led_name):
#         return self.__gpio_obj.blink_led(led_name)

#     def detect_interrupt(self, pin):
#         return self.__gpio_obj.detect_interrupt(pin)


# framework/utilities/os_utils/api_intf_gpio.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from framework.utilities.os_utils.gpio.gpio_linux import GPIOLinux
from framework.utilities.os_utils.gpio.gpio_win import GPIOWindows

class GpioUtilsAPI:
    """
    Unified API wrapper for GPIO operations across Linux and Windows.
    """

    def __init__(self, os_name, platform_obj):
        self.platform_obj = platform_obj
        os_name = os_name.lower()
        if os_name == "linux":
            self.__gpio_obj = GPIOLinux(self.platform_obj)
        elif os_name == "windows":
            self.__gpio_obj = GPIOWindows(self.platform_obj)
        else:
            raise ValueError(f"Unsupported OS: {os_name}")

    def output_toggle(self, pin):
        return self.__gpio_obj.output_toggle(pin)

    def input_read(self, pin):
        return self.__gpio_obj.input_read(pin)

    def led_blink(self, led_name="led0"):
        return self.__gpio_obj.led_blink(led_name)

    def interrupt_detect(self, pin):
        return self.__gpio_obj.interrupt_detect(pin)
