import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from abc import ABC, abstractmethod
from core.logger import setup_logger

class BasePlatform():
    def __init__(self):
        self.logger = setup_logger(self.__class__.__name__)
        self.test_interface_list = []
        self.test_interface_obj = None

    def add_test_interface(self, interface_obj):
        # Logging when interface is created 
        self.logger.info(f"Adding Test Interface: {interface_obj.__classs__.__name__}") # Added info
        self.test_interface_list.append(interface_obj)
        self.test_interface_obj = interface_obj


    def connect_test_interface(self):
        # Logging during connection 
        self.logger.info("Connecting test interface")
        for intf in self.test_interface_list:
            # try/Except for connection.
            try:                                                                    # added info    
                self.logger.info(f"connecting {intf.__class__.__name__}")
                intf.connect()
            except Exception as e:
                self.logger.error(f"Failed to connect interface: {e}")
                raise
    
    def execute(self, command):
        # Safety check before excute
        if not self.test_interface_obj:                                     #added info
            raise Exception ("No test interface configured")
        # Logging command execution
        self.logger.info(f" Executing command : {command}")

        try:                                                                    #added info
            return self.test_interface_obj.execute(command)
        except Exception as e:
            self.logger.error(f"Command execution failed: {e}")
            raise
        