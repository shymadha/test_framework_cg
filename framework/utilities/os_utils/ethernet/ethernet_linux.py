# ethernet_linux.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from framework.utilities.os_utils.ethernet.ethernet_base import EthernetBase

class EthernetLinux(EthernetBase):
    """
    Ethernet utility implementation for Linux platforms.
    Provides methods to detect devices, check link status,
    and test connectivity using Linux-specific commands.
    """

    def __init__(self, platform_obj):
        """
        Initialize the EthernetLinux utility.

        Args:
            platform_obj: Platform object used to execute commands
                          (provides exec_cmd method and logger).
        """
        self.platform_obj = platform_obj

    def detect_device(self):
        """
        Detect available Ethernet devices on Linux.

        Command:
            ip link show

        Returns:
            tuple (output, error, exit_status)
            - output: command stdout with device details
            - error: command stderr or exception message
            - exit_status: 0 if success, non-zero otherwise

        Notes:
            Logs an error if detection fails or output is empty.
        """
        try:
            output, error, exit_status = self.platform_obj.exec_cmd("ip link show", "ssh")
            if exit_status != 0 or not output.strip():
                self.platform_obj.logger.error(f"Ethernet device detection failed: {error}")
            return output, error, exit_status
        except Exception as e:
            self.platform_obj.logger.error(f"Ethernet device detection exception: {e}", exc_info=True)
            return "", str(e), -1

    def check_link_status(self):
        """
        Check the Ethernet link status on Linux.

        Command:
            dmesg | grep -i eth

        Returns:
            tuple (status, error, exit_status)
            - status: "up" if link is active, "down" if inactive,
                      empty string if no status found
            - error: command stderr or exception message
            - exit_status: 0 if success, non-zero otherwise

        Notes:
            Parses output for "up" or "down".
            Logs an error if check fails or output is empty.
        """
        try:
            output, error, exit_status = self.platform_obj.exec_cmd("dmesg | grep -i eth", "ssh")
            if exit_status == 0 and output.strip():
                out = output.strip().lower()
                if "up" in out:
                    return "up", error, exit_status
                elif "down" in out:
                    return "down", error, exit_status
            else:
                self.platform_obj.logger.error(f"Link status check failed: {error}")
            return "", error, exit_status
        except Exception as e:
            self.platform_obj.logger.error(f"Link status check exception: {e}", exc_info=True)
            return "", str(e), -1

    def test_connectivity(self):
        """
        Test network connectivity on Linux.

        Command:
            traceroute google.com

        Returns:
            tuple (output, error, exit_status)
            - output: command stdout (traceroute results)
            - error: command stderr or exception message
            - exit_status: 0 if success, non-zero otherwise

        Notes:
            Logs an error if connectivity test fails.
        """
        try:
            output, error, exit_status = self.platform_obj.exec_cmd("traceroute google.com", "ssh")
            if exit_status != 0:
                self.platform_obj.logger.error(f"Connectivity test failed: {error}")
            return output, error, exit_status
        except Exception as e:
            self.platform_obj.logger.error(f"Connectivity test exception: {e}", exc_info=True)
            return "", str(e), -1
