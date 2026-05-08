# cpu_base.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from framework.utilities.os_utils.os_base import OSBase


class CPUBase(OSBase):
    """
    Abstract base class defining the contract for CPU-related OS utilities.

    This class specifies a unified API for CPU operations such as:
      - Retrieving core count
      - Monitoring usage
      - Running CPU stress tests
      - Querying CPU frequency

    Concrete OS‑specific classes (e.g., CPULinux, CPUWindows) must inherit
    from this base class and implement all defined abstract methods.

    Inherits from
    -------------
    OSBase
        Provides platform execution utilities used by CPU operations.

    Notes
    -----
    Each method raises NotImplementedError by default to enforce
    implementation in derived classes.
    """

    def get_cpu_count(self):
        """
        Retrieve the number of CPU cores available on the system.

        Returns
        -------
        tuple
            A tuple structured as (output, error, status), where:
              - output : str   -> core count or command output
              - error : str    -> error text if applicable
              - status : int   -> command exit code

        Raises
        ------
        NotImplementedError
            Must be implemented by subclasses.
        """
        raise NotImplementedError("Must be implemented in derived classes")

    def monitor_cpu_usage(self):
        """
        Monitor and return the current CPU usage statistics.

        Returns
        -------
        tuple
            (output, error, status) detailing CPU usage output.

        Raises
        ------
        NotImplementedError
            Must be implemented by subclasses.
        """
        raise NotImplementedError("Must be implemented in derived classes")

    def test_cpu_stress(self, timeout="60s"):
        """
        Run a CPU stress test for the specified duration.

        Parameters
        ----------
        timeout : str, optional
            Time duration for the stress test (default "60s").

        Returns
        -------
        tuple
            (output, error, status) representing the stress test result.

        Raises
        ------
        NotImplementedError
            Must be implemented by subclasses.
        """
        raise NotImplementedError("Must be implemented in derived classes")

    def check_cpu_frequency(self):
        """
        Retrieve CPU frequency or scaling information.

        Returns
        -------
        tuple
            (output, error, status) containing CPU frequency details.

        Raises
        ------
        NotImplementedError
            Must be implemented by subclasses.
        """
        raise NotImplementedError("Must be implemented in derived classes")