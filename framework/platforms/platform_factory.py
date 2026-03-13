import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from platforms.beagle_platform import BeaglePlatform
from core.logger import setup_logger         # added 
class PlatformFactory:

    logger = setup_logger("PlatformFactory")                                         # created logger name 

    @staticmethod
    def create_platform(name):                      # creating platform object

        try:                                                                        #added
            PlatformFactory.logger.info(f"Creating platform: {name}")               #added

            if name.lower() == "beagle":
                Platform = BeaglePlatform()                                         #added
                PlatformFactory.logger.info("Beagle platform created successfully") #added
                return BeaglePlatform()

            else:
                PlatformFactory.logger.error(f"unsupported platform: {name}")       #added
                raise ValueError("Unsupported platform")
            
        except Exception as e:                                                      #added
            PlatformFactory.logger.error(f"platform creation failed: {e} ")
            raise
