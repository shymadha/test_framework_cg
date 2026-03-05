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
    def __init__(self,test):
        self.args = self._parse_arguments()
        self.user_config = self._load_config(self.args.config)
        print(f"The self.user_config is {self.user_config} " )
        self.test_file = test
        
        
    def create_obj(self):
        #import pdb;pdb.set_trace()
        interface = InterfaceFactory.create_interface(self.user_config)
        self.platform = PlatformFactory.create_platform(self.user_config["platform"],interface)
        return self.platform
        
    
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

    def _load_config(self, config_path):
        path= Path(config_path).expanduser().resolve()
        if not path.is_file():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with path.open("r") as f:
            return json.load(f)

    def _collect_test_files(self, test_files, test_folder=None):
        collected = []

        if test_files:
            for file in test_files:
                path = Path(file).expanduser().resolve()
                if not path.is_file():
                    raise FileNotFoundError(f"Test file not found: {file}")
                collected.append(path)

        if not collected:
            raise ValueError("No valid test files found.")

        return collected


    def get_test_metadata(self):
        metadata = []
        path = Path(self.test_file).resolve()
        project_root = Path.cwd().resolve()
        relative_path = path.relative_to(project_root)

        module_path = ".".join(
            relative_path.with_suffix("").parts
        )

        class_name = "".join(
            part.capitalize()
            for part in path.stem.split("_")
        )

        metadata.append({
            "module_path": module_path,
            "class_name": class_name
        })

        return metadata

