# ethernet_win.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from framework.utilities.os_utils.ethernet.ethernet_base import EthernetBase

class EthernetWindows(EthernetBase):
    """
    Ethernet utility implementation for Windows platforms.
    Provides methods to detect devices, check link status,
    and test connectivity using Windows-specific commands.
    """

    def __init__(self, platform_obj):
        """
        Initialize the EthernetWindows utility.

        Args:
            platform_obj: Platform object used to execute commands
                          (provides exec_cmd method and logger).
        """
        self.platform_obj = platform_obj

    def detect_device(self):
        """
        Detect available Ethernet devices on Windows.

        Command:
            wmic nic get Name, NetConnectionID, AdapterType, MACAddress

        Returns:
            tuple (output, error, exit_status)
            - output: command stdout with device details
            - error: command stderr or exception message
            - exit_status: 0 if success, non-zero otherwise

        Notes:
            Logs an error if detection fails or output is empty.
        """
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
        """
        Check the Ethernet link status on Windows.

        Command:
            netsh interface show interface

        Returns:
            tuple (status, error, exit_status)
            - status: "up" if connected, "down" if disconnected,
                      empty string if no status found
            - error: command stderr or exception message
            - exit_status: 0 if success, non-zero otherwise

        Notes:
            Parses output for "connected" or "disconnected".
            Logs an error if check fails or output is empty.
        """
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
        """
        Test network connectivity on Windows.

        Command:
            tracert -h 5 -w 1000 google.com
            (limits hops to 5 and timeout to 1 second per hop for faster results)

        Returns:
            tuple (output, error, exit_status)
            - output: command stdout (tracert results)
            - error: command stderr or exception message
            - exit_status: 0 if success, non-zero otherwise

        Notes:
            Logs an error if connectivity test fails.
        """
        try:
            cmd = "tracert -h 5 -w 1000 google.com"
            output, error, exit_status = self.platform_obj.exec_cmd(cmd, "ssh")
            if exit_status != 0:
                self.platform_obj.logger.error(f"Connectivity test failed: {error}")
            return output, error, exit_status
        except Exception as e:
            self.platform_obj.logger.error(f"Connectivity test exception: {e}", exc_info=True)
            return "", str(e), -1
