import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from platforms.base_platform import BasePlatform

class BeaglePlatform(BasePlatform):
    def __init__(self):
        try:

            super().__init__()  # Initialize BasePlatform attributes
            self.boot_time= 20   

            self.logger.info("BaglePlatform initialized")      # baseplatform initilized 
            self.logger.info(f"Boot time set to {self.boot_time} seconds") #--> Boot time set to 20 sec

        except Exception as e:
            self.logger.error(f"failed to initialize BeaglePlatform: {e}")
            raise
    