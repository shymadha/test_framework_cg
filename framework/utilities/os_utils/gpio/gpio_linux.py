# # 
# # framework/utilities/os_utils/gpio/gpio_linux.py
# class GPIOLinux:
#     def __init__(self, platform_obj):
#         self.platform_obj = platform_obj

#     def toggle_output(self, pin):
#         cmds = [
#             f"echo {pin} > /sys/class/gpio/export",
#             f"echo out > /sys/class/gpio/gpio{pin}/direction",
#             f"echo 1 > /sys/class/gpio/gpio{pin}/value",
#             f"echo 0 > /sys/class/gpio/gpio{pin}/value"
#         ]
#         for cmd in cmds:
#             out, err, status = self.platform_obj.exec_cmd(cmd, "ssh")
#             if status != 0:
#                 return out, err, status
#         return "Toggled OK", "", 0

#     def read_input(self, pin):
#         return self.platform_obj.exec_cmd(f"cat /sys/class/gpio/gpio{pin}/value", "ssh")

#     def blink_led(self, led_name):
#         return self.platform_obj.exec_cmd(f"echo timer > /sys/class/leds/{led_name}/trigger", "ssh")

#     def detect_interrupt(self, pin):
#         return self.platform_obj.exec_cmd(f"echo rising > /sys/class/gpio/gpio{pin}/edge", "ssh")


# framework/utilities/os_utils/gpio/gpio_linux.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from framework.utilities.os_utils.gpio.gpio_base import GPIOBase

class GPIOLinux(GPIOBase):
    """
    Linux-specific implementation of GPIO operations using sysfs.
    """

    def __init__(self, platform_obj):
        super().__init__(platform_obj)

    # def output_toggle(self, pin, value=1):
    #     try:
    #         cmds = [
    #             f"echo {pin} > /sys/class/gpio/export",
    #             f"echo out > /sys/class/gpio/gpio{pin}/direction",
    #             f"echo {value} > /sys/class/gpio/gpio{pin}/value"
    #         ]
    #         for cmd in cmds:
    #             out, err, status = self.platform_obj.exec_cmd(cmd, "ssh")
    #             if status != 0:
    #                 return out, err, status
    #         return f"GPIO {pin} toggled to {value}", "", 0
    #     except Exception as e:
    #         return "", str(e), -1
    def output_toggle(self, pin, value=1):

        try:
            GPIO_PATH = f"/sys/class/gpio/gpio{pin}"
    
            # Export only if not already exported
            export_cmd = (
                f"[ -d {GPIO_PATH} ] || "
                f"echo {pin} | sudo tee /sys/class/gpio/export"
            )
    
            cmds = [
                export_cmd,
                f"echo out | sudo tee {GPIO_PATH}/direction",
                f"echo {value} | sudo tee {GPIO_PATH}/value",
            ]
    
            for cmd in cmds:
                out, err, status = self.platform_obj.exec_cmd(cmd, "ssh")
                if status != 0:
                    return out, err, status
    
            return f"GPIO {pin} toggled to {value}", "", 0
    
        except Exception as e:
            return "", str(e), -1

    def input_read(self, pin):
        try:
            return self.platform_obj.exec_cmd(f"cat /sys/class/gpio/gpio{pin}/value", "ssh")
        except Exception as e:
            return "", str(e), -1

    def led_blink(self, led_name="led0"):
        try:
            return self.platform_obj.exec_cmd(f"echo timer > /sys/class/leds/{led_name}/trigger", "ssh")
        except Exception as e:
            return "", str(e), -1

    def interrupt_detect(self, pin):
        try:
            return self.platform_obj.exec_cmd(f"echo rising > /sys/class/gpio/gpio{pin}/edge", "ssh")
        except Exception as e:
            return "", str(e), -1
