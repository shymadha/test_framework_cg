# parse_user_input.py

import argparse
import json
from pathlib import Path
import sys
import os
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from platforms.platform_factory import PlatformFactory
from interfaces.interface_factory import InterfaceFactory

class ParseUserInput:
    def __init__(self):
        self.args = self._parse_arguments()
        self.user_input = self.parse_user_input(self.args.config)
   
    def parse_user_input(self, config_file):
        with open(config_file) as f:
            self.user_input = json.load(f)
        return self.user_input

    def __create_platform_obj(self):
        platform_name = self.user_input.get("SUT", [{}])[0].get("platform", None)
        platform_obj = PlatformFactory.create_platform(platform_name)
        return platform_obj
        
    def create_dev_obj(self):
        self.platform_obj = self.__create_platform_obj()
        interfaces = self.user_input.get("SUT", [{}])[0].get("interfaces", [])

        for intf_cfg in interfaces:
            intf_type = intf_cfg.get("type")
            interface_obj = InterfaceFactory.create_test_intf(intf_cfg)
            self.platform_obj.add_test_interface(interface_obj, intf_cfg.get("type"))
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
    
    
    def parse_int_output(self,output):
        if isinstance(output, int):
            return output

        if not isinstance(output, str):
            raise ValueError(f"Unexpected type: {type(output)}")

        # Extract only the numbers from the string
        match = re.search(r'\d+', output)
        if not match:
            raise ValueError(f"No integer found in output: {output!r}")

        return int(match.group())
   
