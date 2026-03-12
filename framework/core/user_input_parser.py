# parse_user_input.py

import argparse
import json
from pathlib import Path
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from platforms.platform_factory import PlatformFactory
from interfaces.interface_factory import InterfaceFactory

class ParseUserInput:
    def __init__(self):
        self.args = self._parse_arguments()
        self.user_input = None
   
    def parse_user_input(self, config_file):
        with open(config_file) as f:
            self.user_input = json.load(f)
        return self.user_input

    def __create_platform_obj(self):
        platform_name = self.user_input["SUT"][0]["platform"]
        platform_obj = PlatformFactory.create_platform(platform_name)
        return platform_obj
        
        
    def create_dev_obj(self,user_input_dict):
        self.platform_obj = self.__create_platform_obj()
        test_interface = InterfaceFactory.create_interface(user_input_dict)
        self.platform_obj.add_test_interface(test_interface)
        self.platform_obj.connect_test_interface()
    
    def _parse_arguments(self):
        parser = argparse.ArgumentParser(
            description="Test Runner CLI"
        )

        parser.add_argument(
            "--config",
            required=True,
            help="Path to configuration JSON file"
        )

        return parser.parse_args()

    def get_platform_obj(self):
        return self.platform_obj

    
