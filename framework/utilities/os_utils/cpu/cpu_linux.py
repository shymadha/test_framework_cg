# cpu_linux.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from framework.utilities.os_utils.os_base import OSBase
from framework.utilities.os_utils.cpu.cpu_base import CPUBase


class CPULinux(CPUBase):
    """
    Linux-specific implementation of CPU operations.

    This class provides concrete implementations of CPU-related utilities for
    Linux-based platforms. It relies on common Linux tools such as:
      - `nproc` for core count
      - `top` and `grep` for CPU usage
      - Python one-liner for stress testing
      - `lscpu` for frequency and vendor information

    All CPU interactions are executed through the platform object's
    `exec_cmd()` method, typically over SSH.

    Inherits from
    -------------
    CPUBase
        Defines the abstract interface that all CPU utility classes must implement.
    """

    def get_cpu_count(self):
        """
        Retrieve the number of CPU cores from a Linux system using `nproc`.

        Returns
        -------
        tuple
            (output, error, exit_status):
              - output : str  -> number of cores
              - error : str   -> stderr (if any)
              - exit_status : int -> command status code

        Notes
        -----
        - Logs an error if the command fails.
        - Returns (-1) status on unexpected exceptions.
        """
        try:
            output, error, exit_status = self.platform_obj.exec_cmd("nproc", "ssh")
            if exit_status != 0:
                self.platform_obj.logger.error(f"CPU Core count error: {error}")
            return output, error, exit_status
        except Exception as e:
            self.platform_obj.logger.error(
                f"CPU Core count exception: {e}", exc_info=True
            )
            return "", str(e), -1

    def monitor_cpu_usage(self):
        """
        Capture CPU usage statistics using `top -b -n 1`.

        Returns
        -------
        tuple
            (output, error, exit_status) where:
              - output includes CPU usage line from top
              - error contains stderr output
              - exit_status indicates success/failure

        Notes
        -----
        - Uses grep to isolate the `Cpu(s)` line.
        - Logs errors on failure.
        """
        try:
            output, error, exit_status = self.platform_obj.exec_cmd(
                "top -b -n 1 | grep 'Cpu(s)'", "ssh"
            )
            if exit_status != 0:
                self.platform_obj.logger.error(
                    f"CPU Usage Monitoring failed: {error}"
                )
            return output, error, exit_status
        except Exception as e:
            self.platform_obj.logger.error(
                f"CPU Usage Monitoring exception: {e}", exc_info=True
            )
            return "", str(e), -1

    def test_cpu_stress(self, timeout="10s"):
        """
        Execute a CPU stress workload for the specified duration.

        Parameters
        ----------
        timeout : str, optional
            Duration for which the CPU should be stressed (default "10s").
            Must contain at least one digit.

        Returns
        -------
        tuple
            (output, error, exit_status) from executing the stress command.

        Notes
        -----
        - Extracts seconds from the timeout string.
        - Uses a Python one-liner to load CPU for the given duration.
        - Logs errors and exceptions.
        """
        try:
            import re
            match = re.search(r"\d+", str(timeout))
            seconds = int(match.group(0)) if match else 10

            stress_cmd = (
                "python3 -c \"import time; end=time.time()+"
                f"{seconds}; all(1+1 for _ in iter(lambda: time.time()<end, False))\""
            )

            output, error, exit_status = self.platform_obj.exec_cmd(
                stress_cmd, "ssh"
            )

            if exit_status != 0:
                self.logger.error(f"CPU Stress Testing failed: {error}")

            return output, error, exit_status

        except Exception as e:
            self.logger.error(
                f"CPU Stress Testing exception: {e}", exc_info=True
            )
            return "", str(e), -1

    def check_cpu_frequency(self):
        """
        Retrieve CPU frequency information using `lscpu`.

        Returns
        -------
        tuple
            (output, error, exit_status):
              - `output` usually contains frequency data in MHz
              - `error` contains stderr (if any)
              - `exit_status` indicates success/failure

        Notes
        -----
        - Uses grep to extract relevant lines.
        """
        try:
            output, error, exit_status = self.platform_obj.exec_cmd(
                "lscpu | grep 'MHz'", "ssh"
            )
            if exit_status != 0:
                self.logger.error(
                    f"CPU Frequency Scaling Check failed: {error}"
                )
            return output, error, exit_status
        except Exception as e:
            self.logger.error(
                f"CPU Frequency Scaling Check exception: {e}",
                exc_info=True
            )
            return "", str(e), -1

    def get_cpu_vendor(self):
        """
        Retrieve CPU vendor information using `lscpu`.

        Returns
        -------
        tuple
            (output, error, exit_status) similar to other commands.

        Notes
        -----
        - Uses grep for extracting 'Vendor ID'.
        - Logs errors and exceptions for debugging.
        """
        try:
            output, error, exit_status = self.platform_obj.exec_cmd(
                "lscpu | grep 'Vendor ID'", "ssh"
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