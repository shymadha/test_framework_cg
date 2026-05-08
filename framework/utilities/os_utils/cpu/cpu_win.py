# cpu_win.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from framework.utilities.os_utils.os_base import OSBase
from framework.utilities.os_utils.cpu.cpu_base import CPUBase


class CPUWindows(CPUBase):
    """
    Windows-specific implementation of CPU utilities.

    This class provides concrete CPU operations for Windows-based systems.
    It interacts with standard Windows CLI tools such as:

      - `wmic` for CPU core count, frequency, vendor details
      - `typeperf` for live CPU usage metrics
      - PowerShell for CPU stress testing

    All commands execute on the target system through the platform object's
    `exec_cmd()` method (typically via SSH for remote devices).

    Inherits from
    -------------
    CPUBase
        The abstract base defining required CPU utility methods.
    """

    def get_cpu_count(self):
        """
        Retrieve the number of CPU cores on Windows using WMIC.

        Returns
        -------
        tuple
            (output, error, exit_status):
              - output : str  -> Number of CPU cores as reported by WMIC
              - error : str   -> stderr output if command fails
              - exit_status : int -> Command exit code

        Notes
        -----
        - Logs an error if WMIC fails.
        - Returns status -1 on unexpected exceptions.
        """
        try:
            output, error, exit_status = self.platform_obj.exec_cmd(
                "wmic cpu get NumberOfCores", "ssh"
            )
            if exit_status != 0:
                self.platform_obj.logger.error(f"CPU core count failed: {error}")
            return output, error, exit_status
        except Exception as e:
            self.platform_obj.logger.error(
                f"CPU core count exception: {e}", exc_info=True
            )
            return "", str(e), -1

    def monitor_cpu_usage(self):
        """
        Monitor and retrieve CPU usage using Windows 'typeperf'.

        Returns
        -------
        tuple
            (output, error, exit_status):
              - output : str  -> Performance counter readings
              - error : str   -> stderr output if typeperf fails
              - exit_status : int -> Command status code

        Notes
        -----
        - Uses the `\\Processor(_Total)\\% Processor Time` counter.
        - Logs failures and exceptions for diagnostics.
        """
        try:
            output, error, exit_status = self.platform_obj.exec_cmd(
                'typeperf "\\Processor(_Total)\\% Processor Time" -sc 1', "ssh"
            )
            if exit_status != 0:
                self.platform_obj.logger.error(f"CPU Usage Monitoring failed: {error}")
            return output, error, exit_status
        except Exception as e:
            self.platform_obj.logger.error(
                f"CPU Usage Monitoring exception: {e}", exc_info=True
            )
            return "", str(e), -1

    def test_cpu_stress(self, timeout="60s"):
        """
        Execute a CPU stress workload using PowerShell.

        Parameters
        ----------
        timeout : str, optional
            Duration for the stress test (default "60s").
            Extractable integer value is interpreted as seconds.

        Returns
        -------
        tuple
            (output, error, exit_status) from PowerShell command execution.

        Notes
        -----
        - Runs a simple loop repeatedly performing arithmetic operations.
        - Logs failures and exceptions for debugging.
        """
        try:
            import re
            match = re.search(r"\d+", str(timeout))
            seconds = int(match.group(0)) if match else 10

            ps_command = (
                f"$stop = (Get-Date).AddSeconds({seconds}); "
                f"while ((Get-Date) -lt $stop) {{ 1 + 1 }}"
            )

            output, error, exit_status = self.platform_obj.exec_cmd(
                f'powershell -command "{ps_command}"', "ssh"
            )

            if exit_status != 0:
                self.platform_obj.logger.error(f"CPU Stress Testing failed: {error}")

            return output, error, exit_status

        except Exception as e:
            self.platform_obj.logger.error(
                f"CPU Stress Testing exception: {e}", exc_info=True
            )
            return "", str(e), -1

    def check_cpu_frequency(self):
        """
        Retrieve CPU frequency and clock speed data using WMIC.

        Returns
        -------
        tuple
            (output, error, exit_status):
              - output : str -> Includes name, current, and max clock speed
              - error : str  -> Error output
              - exit_status : int -> Command result

        Notes
        -----
        - Provides frequency information in MHz.
        """
        try:
            output, error, exit_status = self.platform_obj.exec_cmd(
                "wmic cpu get name,CurrentClockSpeed,MaxClockSpeed", "ssh"
            )
            if exit_status != 0:
                self.platform_obj.logger.error(
                    f"CPU Frequency Scaling Check failed: {error}"
                )
            return output, error, exit_status
        except Exception as e:
            self.platform_obj.logger.error(
                f"CPU Frequency Scaling Check exception: {e}", exc_info=True
            )
            return "", str(e), -1

    def get_cpu_vendor(self):
        """
        Retrieve CPU vendor/manufacturer information using WMIC.

        Returns
        -------
        tuple
            (output, error, exit_status):
              - output : str -> Vendor name (e.g., Intel, AMD)
              - error : str  -> stderr output
              - exit_status : int -> Command status code

        Notes
        -----
        - Logs failures and exceptions for traceability.
        """
        try:
            output, error, exit_status = self.platform_obj.exec_cmd(
                "wmic cpu get manufacturer", "ssh"
            )
            if exit_status != 0:
                self.platform_obj.logger.error(
                    f"CPU Vendor Detection failed: {error}"
                )
            return output, error, exit_status
        except Exception as e:
            self.platform_obj.logger.error(
                f"CPU Vendor Detection exception: {e}", exc_info=True
            )
            return "", str(e), -1