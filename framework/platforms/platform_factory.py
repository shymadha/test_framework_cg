import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from platforms.beagle_platform import BeaglePlatform
class PlatformFactory:

    @staticmethod
    def create_platform(name, interface):

        if name.lower() == "beagle":
            return BeaglePlatform(interface)

        else:
            raise ValueError("Unsupported platform")