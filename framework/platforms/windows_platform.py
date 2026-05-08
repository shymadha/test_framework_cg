import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from platforms.base_platform import BasePlatform


class WindowsPlatform(BasePlatform):
    """
    Platform implementation for Windows-based systems.

    This class extends BasePlatform to represent a local Windows host.
    It inherits all platform management functionality such as interface
    handling, OS detection, and command execution.

    Attributes
    ----------
    boot_time : int
        Estimated boot time in seconds for the Windows platform.
    """

    def __init__(self):
        """
        Initialize the WindowsPlatform with default properties.

        Calls BasePlatform initializer and sets Windows-specific attributes.
        """
        super().__init__()
        self.os_type = "windows"
        self.boot_time = 30
