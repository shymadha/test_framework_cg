# ethernet_base.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from framework.utilities.os_utils.os_base import OSBase

class EthernetBase(OSBase):
    """
    Abstract base class for Ethernet utilities.
    Defines the interface for Ethernet operations that must
    be implemented in platform-specific subclasses (Linux, Windows).
    """

    def detect_device(self):
        """
        Detect available Ethernet devices.

        This method must be implemented in derived classes
        (e.g., EthernetLinux, EthernetWindows) to run the
        appropriate system command for the platform.

        Raises:
            NotImplementedError: Always, unless overridden in subclass.
        """
        raise NotImplementedError("Must be implemented in derived classes")

    def check_link_status(self):
        """
        Check the Ethernet link status.

        This method must be implemented in derived classes
        to determine whether the Ethernet link is up or down
        using platform-specific commands.

        Raises:
            NotImplementedError: Always, unless overridden in subclass.
        """
        raise NotImplementedError("Must be implemented in derived classes")

    def test_connectivity(self):
        """
        Test network connectivity.

        This method must be implemented in derived classes
        to verify connectivity (e.g., using ping or traceroute)
        depending on the operating system.

        Raises:
            NotImplementedError: Always, unless overridden in subclass.
        """
        raise NotImplementedError("Must be implemented in derived classes")
