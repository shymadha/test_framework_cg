
# ethernet_win.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from framework.utilities.os_utils.ethernet.ethernet_base import EthernetBase

class EthernetWindows(EthernetBase):
    def __init__(self, platform_obj):
        self.platform_obj = platform_obj

    def detect_device(self):
        try:
            cmd = "wmic nic get Name, NetConnectionID, AdapterType, MACAddress"
            output, error, exit_status = self.platform_obj.exec_cmd(cmd, "ssh")
            if exit_status != 0 or not output.strip():
                self.platform_obj.logger.error(f"Ethernet device detection failed: {error}")
            return output, error, exit_status
        except Exception as e:
            self.platform_obj.logger.error(f"Ethernet device detection exception: {e}", exc_info=True)
            return "", str(e), -1

    def check_link_status(self):
        try:
            cmd = "netsh interface show interface"
            output, error, exit_status = self.platform_obj.exec_cmd(cmd, "ssh")
            if exit_status == 0 and output.strip():
                out = output.strip().lower()
                if "connected" in out:
                    return "up", error, exit_status
                elif "disconnected" in out:
                    return "down", error, exit_status
            else:
                self.platform_obj.logger.error(f"Link status check failed: {error}")
            return "", error, exit_status
        except Exception as e:
            self.platform_obj.logger.error(f"Link status check exception: {e}", exc_info=True)
            return "", str(e), -1

    def test_connectivity(self):
        try:
            cmd = "tracert google.com"
            output, error, exit_status = self.platform_obj.exec_cmd(cmd, "ssh")
            if exit_status != 0:
                self.platform_obj.logger.error(f"Connectivity test failed: {error}")
            return output, error, exit_status
        except Exception as e:
            self.platform_obj.logger.error(f"Connectivity test exception: {e}", exc_info=True)
            return "", str(e), -1
