import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from abc import ABC, abstractmethod
from core.logger import setup_logger

class BasePlatform():
    def __init__(self):
        self.logger = setup_logger(self.__class__.__name__)
        self.test_interfaces = {}
        self.os_type = None

    def add_test_interface(self, interface_obj,interface_type):
        if not interface_type:
            raise ValueError("Interface type must be provided")
        self.test_interfaces[interface_type] = interface_obj

    def connect_test_interface(self):
        for intf in self.test_interfaces.values():
            intf.connect()
    
    def exec_cmd(self, command,interface_type=None):
        intf = None
        if interface_type:
            intf = self.test_interfaces.get(interface_type)

        if intf:
            return intf.execute(command)
        else:
            raise ValueError(f"Interface {interface_type} not found")

        return self.test_interface_obj.execute(command)
        
    
    def detect_os(self):
        output, error, status = self.exec_cmd("uname","ssh")
        if status == 0:
            if "Linux" in output:
                self.os_type = "linux"
            elif "Darwin" in output:
                self.os_type = "mac"
        else:
            output, error, status = self.exec_cmd("ver","ssh")
            if "Windows" in output:
                self.os_type = "windows"

        self.logger.info(f"Detected OS: {self.os_type}")
        return self.os_type
    
    def get_os_type(self):
        if self.os_type is None:
            self.detect_os()
        return self.os_type
    
    def close(self):
        for intf in self.test_interfaces.values():
            intf.close()
        