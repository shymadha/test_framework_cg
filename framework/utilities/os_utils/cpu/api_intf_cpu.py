# api_intf_cpu.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from framework.utilities.os_utils.cpu.cpu_win import CPUWindows
from framework.utilities.os_utils.cpu.cpu_linux import CPULinux


class CpuUtilsAPI:
    """
    Unified API wrapper for CPU-related operations across multiple operating systems.

    This class abstracts OS-specific CPU implementations and exposes a
    common interface for:
      - Retrieving CPU core count
      - Monitoring CPU usage
      - Triggering CPU stress tests
      - Checking frequency scaling
      - Querying CPU vendor information

    Based on the detected OS (`windows` or `linux`), it internally
    instantiates either `CPUWindows` or `CPULinux`, while providing
    a consistent interface to the rest of the framework.

    Attributes
    ----------
    platform_obj : object
        Platform object representing the target device/system.
    os_name : str
        Operating system name (e.g., "windows", "linux").
    __cpu_utils_obj : CPUWindows or CPULinux
        Concrete CPU utility implementation selected by OS.
    """

    def __init__(self, os_name, platform_obj):
        """
        Initialize CPU utilities API with OS-specific implementation.

        Parameters
        ----------
        os_name : str
            Name of the OS ("windows" or "linux") used to choose
            the appropriate backend class.
        platform_obj : object
            The active platform object that provides command execution.

        Raises
        ------
        ValueError
            If the OS name is unsupported or unrecognized.
        """
        self.platform_obj = platform_obj
        self.os_name = os_name

        if self.os_name.lower() == "windows":
            self.__cpu_utils_obj = CPUWindows(self.platform_obj)

        elif self.os_name.lower() == "linux":
            self.__cpu_utils_obj = CPULinux(self.platform_obj)

        else:
            raise ValueError(f"Unsupported OS: {self.os_name}")

    def get_core_count(self):
        """
        Retrieve the number of CPU cores available on the system.

        Returns
        -------
        tuple
            A tuple (output, error, status) returned by the underlying
            OS-specific implementation.
        """
        return self.__cpu_utils_obj.get_cpu_count()

    def monitor_cpu_usage(self):
        """
        Monitor and retrieve current CPU usage statistics.

        Returns
        -------
        tuple
            (output, error, status) containing CPU usage details and
            command execution status.
        """
        return self.__cpu_utils_obj.monitor_cpu_usage()

    def test_cpu_stress(self, timeout="60s"):
        """
        Run a CPU stress workload for a specified duration.

        Parameters
        ----------
        timeout : str, optional
            Duration for the stress test (default "60s").

        Returns
        -------
        tuple
            (output, error, status) reflecting test execution results.
        """
        return self.__cpu_utils_obj.test_cpu_stress(timeout)

    def check_cpu_frequency(self):
        """
        Retrieve CPU frequency and clock scaling information.

        Returns
        -------
        tuple
            (output, error, status) containing frequency details.
        """
        return self.__cpu_utils_obj.check_cpu_frequency()

    def get_cpu_vendor(self):
        """
        Identify and return CPU vendor information.

        Returns
        -------
        tuple
            (output, error, status) with vendor string and command status.
        """
        return self.__cpu_utils_obj.get_cpu_vendor()