# ethernet_base.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from framework.utilities.os_utils.os_base import OSBase


class EthernetBase(OSBase):
    """
    Abstract base class defining Ethernet-related OS utility operations.

    This class establishes a standard interface for all Ethernet/network
    utilities implemented across different operating systems. Concrete
    subclasses such as `EthernetLinux` and `EthernetWindows` must implement
    the methods defined here to ensure consistent Ethernet behavior across
    the framework.

    Typical operations include:
      - Detecting available Ethernet interfaces
      - Checking Ethernet link status (UP/DOWN)
      - Testing network connectivity to external hosts or gateways

    Inherits from
    -------------
    OSBase
        Provides command execution support for OS-specific implementations.

    Notes
    -----
    Each method raises NotImplementedError by default to enforce proper
    implementation in derived subclasses.
    """

    def detect_device(self):
        """
        Detect available Ethernet devices or interfaces on the system.

        Returns
        -------
        tuple
            OS-specific response in the format (output, error, exit_status).

        Raises
        ------
        NotImplementedError
            Must be implemented in subclass (e.g., EthernetLinux, EthernetWindows).
        """
        raise NotImplementedError("Must be implemented in derived classes")

    def check_link_status(self):
        """
        Check the operational link status of the Ethernet interface.

        Returns
        -------
        tuple
            (output, error, exit_status), where:
              - output may contain 'UP', 'DOWN', or equivalent status text
              - error contains stderr output if any
              - exit_status indicates command execution success/failure

        Raises
        ------
        NotImplementedError
            Must be implemented in subclass.
        """
        raise NotImplementedError("Must be implemented in derived classes")

    def test_connectivity(self):
        """
        Perform a network connectivity test using the Ethernet interface.

        This may include:
          - pinging well-known hosts
          - performing DNS resolution
          - issuing HTTP/HTTPS requests depending on OS implementation

        Returns
        -------
        tuple
            (output, error, exit_status) with OS-specific connectivity results.

        Raises
        ------
        NotImplementedError
            Must be implemented in subclass.
        """
        raise NotImplementedError("Must be implemented in derived classes")