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
        self.test_interface_list.append(interface_obj)
        self.test_interface_obj = interface_obj


    def connect_test_interface(self):
        for intf in self.test_interface_list:
            intf.connect()
    
    def execute(self, command):
        return self.test_interface_obj.execute(command)