import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from abc import ABC, abstractmethod
from core.logger import setup_logger

class BasePlatform():
    def __init__(self, interface):
        self.interface = interface
        self.logger = setup_logger(self.__class__.__name__)

    def setup(self):
        self.logger.info("Setting up Beagle")
        self.interface.connect()

    
    def cleanup(self):
        self.logger.info("Cleaning up Beagle")
        self.interface.close()