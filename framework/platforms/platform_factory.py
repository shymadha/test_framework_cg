import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from platforms.beagle_platform import BeaglePlatform


class PlatformFactory:
    """
    Factory class responsible for constructing platform objects.

    The platform factory abstracts platform creation logic, enabling the
    test framework to dynamically instantiate platform-specific classes
    based on the configuration provided in the testbed JSON.

    Supported platforms:
      - "beagle" → BeaglePlatform

    Additional platforms can be added by extending the factory logic.
    """

    @staticmethod
    def create_platform(name):
        """
        Create and return a platform object based on the given platform name.

        Parameters
        ----------
        name : str
            Name of the platform as provided in the test configuration
            (e.g., "beagle").

        Returns
        -------
        BasePlatform
            Instance of a concrete platform class (e.g., BeaglePlatform).

        Raises
        ------
        ValueError
            If the platform name is unsupported or unrecognized.
        """
        if name.lower() == "beagle":
            return BeaglePlatform()

        else:
            raise ValueError("Unsupported platform")