import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from platforms.base_platform import BasePlatform

class BeaglePlatform(BasePlatform):
    def __init__(self,interface):
        super().__init__(interface)  # Initialize BasePlatform attributes
        self.boot_time= 20
    