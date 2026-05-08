import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from platforms.base_platform import BasePlatform


class BeaglePlatform(BasePlatform):
    """
    Platform implementation for BeagleBoard‑based systems.

    This class extends the BasePlatform to represent a BeagleBoard or
    BeagleBone‑class device (e.g., BeagleBone Black, BeagleBone AI, etc.).
    It inherits all platform management functionality such as interface
    handling, OS detection, and command execution.

    Attributes
    ----------
    boot_time : int
        Estimated boot time in seconds for the Beagle platform.
        Useful for automation workflows that need predictable delays.
    """

    def __init__(self):
        """
        Initialize the BeaglePlatform with default properties.

        Calls BasePlatform initializer and sets Beagle-specific timing values.
        """
        super().__init__()  # Initialize BasePlatform attributes
        self.boot_time = 20