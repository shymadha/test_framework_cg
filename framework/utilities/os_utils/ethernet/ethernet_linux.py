# ethernet_linux.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from framework.utilities.os_utils.ethernet.ethernet_base import EthernetBase


class EthernetLinux(EthernetBase):
    """
    Linux-specific implementation of Ethernet utility operations.

    This class provides concrete Ethernet-related features designed for
    Linux systems. Operations rely on standard networking tools such as:
      - `ip link show` to enumerate Ethernet interfaces
      - `dmesg` logs to determine link status messages
      - `traceroute` to verify external connectivity

    All commands are executed through the platform object's `exec_cmd()`
    method (commonly over SSH).

    Inherits from
    -------------
    EthernetBase
        Defines the abstract interface for Ethernet utilities.
    """

    def __init__(self, platform_obj):
        """
        Initialize Linux Ethernet utilities with a platform execution object.

        Parameters
        ----------
        platform_obj : object
            Platform object responsible for executing commands on the target
            device or system.
        """
        self.platform_obj = platform_obj

    def detect_device(self):
        """
        Detect available Ethernet interfaces using `ip link show`.

        Returns
        -------
        tuple
            (output, error, exit_status) where:
              - output contains the raw link/interface list
              - error contains stderr (if any)
              - exit_status indicates success or failure

        Notes
        -----
        - Logs an error when no output is returned or command fails.
        """
        try:
            output, error, exit_status = self.platform_obj.exec_cmd(
                "ip link show", "ssh"
            )
            if exit_status != 0 or not output.strip():
                self.platform_obj.logger.error(
                    f"Ethernet device detection failed: {error}"
                )
            return output, error, exit_status
        except Exception as e:
            self.platform_obj.logger.error(
                f"Ethernet device detection exception: {e}", exc_info=True
            )
            return "", str(e), -1

    def check_link_status(self):
        """
        Determine current Ethernet link status using kernel log messages.

        This method greps `dmesg` for Ethernet-related messages and attempts
        to classify link status as `"up"` or `"down"`.

        Returns
        -------
        tuple
            (status, error, exit_status) where:
              - status : str -> "up", "down", or empty string if undetermined
              - error  : str -> stderr output
              - exit_status : int -> return code of the executed command

        Notes
        -----
        - Returns a lowercase status.
        - Logs errors and exceptions for debugging.
        """
        try:
            output, error, exit_status = self.platform_obj.exec_cmd(
                "dmesg | grep -i eth", "ssh"
            )

            if exit_status == 0 and output.strip():
                out = output.strip().lower()

                if "up" in out:
                    return "up", error, exit_status
                elif "down" in out:
                    return "down", error, exit_status

            else:
                self.platform_obj.logger.error(
                    f"Link status check failed: {error}"
                )

            return "", error, exit_status

        except Exception as e:
            self.platform_obj.logger.error(
                f"Link status check exception: {e}", exc_info=True
            )
            return "", str(e), -1

    def test_connectivity(self):
        """
        Test external network connectivity using `traceroute`.

        By default, it attempts to reach `google.com`, providing visibility
        into routing, DNS, and gateway behavior.

        Returns
        -------
        tuple
            (output, error, exit_status) where:
              - output contains traceroute hops or diagnostic messages
              - error contains stderr output
              - exit_status indicates success or failure

        Notes
        -----
        - Logs failures and exceptions.
        """
        try:
            output, error, exit_status = self.platform_obj.exec_cmd(
                "traceroute google.com", "ssh"
            )

            if exit_status != 0:
                self.platform_obj.logger.error(
                    f"Connectivity test failed: {error}"
                )

            return output, error, exit_status

        except Exception as e:
            self.platform_obj.logger.error(
                f"Connectivity test exception: {e}", exc_info=True
            )
            return "", str(e), -1