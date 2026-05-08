# ethernet_win.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from framework.utilities.os_utils.ethernet.ethernet_base import EthernetBase


class EthernetWindows(EthernetBase):
    """
    Windows-specific implementation of Ethernet utility operations.

    This class provides concrete Ethernet-related features for Windows
    systems. It uses standard Windows networking tools such as:
      - `wmic` for listing NIC devices
      - `netsh` for retrieving connection/link status
      - `tracert` for connectivity verification

    All commands are executed through the platform object using its
    `exec_cmd()` API, typically over SSH for remote Windows hosts.

    Inherits from
    -------------
    EthernetBase
        Abstract base class defining the contract for all Ethernet utilities.
    """

    def __init__(self, platform_obj):
        """
        Initialize the Ethernet utility with a platform execution object.

        Parameters
        ----------
        platform_obj : object
            Platform object responsible for executing commands on the target
            Windows machine.
        """
        self.platform_obj = platform_obj

    def detect_device(self):
        """
        Detect Ethernet network interfaces using WMIC.

        Returns
        -------
        tuple
            (output, error, exit_status) where:
              - output : str -> NIC name, MAC address, adapter type, etc.
              - error : str  -> stderr output
              - exit_status : int -> return code of the executed command

        Notes
        -----
        - Logs an error if WMIC command fails or returns empty results.
        """
        try:
            cmd = "wmic nic get Name, NetConnectionID, AdapterType, MACAddress"
            output, error, exit_status = self.platform_obj.exec_cmd(cmd, "ssh")

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
        Check the Ethernet link state using Windows `netsh`.

        Inspects the output of:
            netsh interface show interface

        to determine if the interface is "connected" or "disconnected".

        Returns
        -------
        tuple
            (status, error, exit_status) where:
              - status : str -> "up", "down", or empty string if unknown
              - error : str  -> stderr output
              - exit_status : int -> result of the executed command

        Notes
        -----
        - Converts output to lowercase and searches for keywords.
        - Logs errors for diagnostic purposes.
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
        Test external network connectivity using Windows `tracert`.

        Executes:
            tracert -h 5 -w 1000 google.com

        to verify routing path and basic external reachability.

        Returns
        -------
        tuple
            (output, error, exit_status) where:
              - output : str -> traceroute hops and diagnostics
              - error  : str -> stderr output
              - exit_status : int -> success/failure state

        Notes
        -----
        - Logs detailed errors on command failure.
        """
        try:
            cmd = "tracert -h 5 -w 1000 google.com"
            output, error, exit_status = self.platform_obj.exec_cmd(cmd, "ssh")

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