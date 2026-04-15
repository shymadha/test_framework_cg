# # # gpio_base.py
# # import sys
# # import os

# # sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# # from framework.utilities.os_utils.os_base import OSBase

# # class GPIOBase(OSBase):
# #     """
# #     Abstract base class defining GPIO-related OS utility operations.
# #     """

# #     def output_toggle(self, pin, value):
# #         raise NotImplementedError("Must be implemented in derived classes")

# #     def input_read(self, pin):
# #         raise NotImplementedError("Must be implemented in derived classes")

# #     def led_blink(self, led_name="led0"):
# #         raise NotImplementedError("Must be implemented in derived classes")

# #     def interrupt_detect(self, pin):
# #         raise NotImplementedError("Must be implemented in derived classes")


# # gpio_base.py
# import sys
# import os

# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# from framework.utilities.os_utils.os_base import OSBase

# class GPIOBase(OSBase):
#     """
#     Abstract base class defining GPIO-related OS utility operations.

#     All methods must return a tuple (output, error, status) where:
#       - output : str   -> command output or result
#       - error  : str   -> error message if any
#       - status : int   -> exit code (0 = success)
#     """

#     def output_toggle(self, pin, value):
#         """
#         Toggle a GPIO output pin.

#         Parameters
#         ----------
#         pin : int
#             GPIO pin number.
#         value : int
#             Desired value (0 or 1).
#         """
#         raise NotImplementedError("Must be implemented in derived classes")

#     def input_read(self, pin):
#         """
#         Read the value of a GPIO input pin.

#         Parameters
#         ----------
#         pin : int
#             GPIO pin number.
#         """
#         raise NotImplementedError("Must be implemented in derived classes")

#     def led_blink(self, led_name="led0"):
#         """
#         Trigger LED blink on the specified LED.

#         Parameters
#         ----------
#         led_name : str, optional
#             LED device name (default 'led0').
#         """
#         raise NotImplementedError("Must be implemented in derived classes")

#     def interrupt_detect(self, pin):
#         """
#         Configure and detect GPIO interrupt/edge events.

#         Parameters
#         ----------
#         pin : int
#             GPIO pin number.
#         """
#         raise NotImplementedError("Must be implemented in derived classes")


# framework/utilities/os_utils/gpio/gpio_base.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from framework.utilities.os_utils.os_base import OSBase

class GPIOBase(OSBase):
    """
    Abstract base class defining GPIO-related OS utility operations.
    All methods must return (output, error, status).
    """

    def output_toggle(self, pin, value=1):
        """
        Toggle a GPIO output pin.
        """
        raise NotImplementedError("Must be implemented in derived classes")

    def input_read(self, pin):
        """
        Read the value of a GPIO input pin.
        """
        raise NotImplementedError("Must be implemented in derived classes")

    def led_blink(self, led_name="led0"):
        """
        Trigger LED blink on the specified LED.
        """
        raise NotImplementedError("Must be implemented in derived classes")

    def interrupt_detect(self, pin):
        """
        Configure and detect GPIO interrupt/edge events.
        """
        raise NotImplementedError("Must be implemented in derived classes")
