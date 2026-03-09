import json
from pathlib import Path
import os
import sys
import importlib
import argparse
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from framework.core.user_input_parser import ParseUserInput
class TestbedUtils:
    def __init__(self, config_path=None):
        if config_path is None:
            # Default to userinput/testbed.json relative to project root
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "userinput" / "testbed.json"
        
        self.config_path = Path(config_path).resolve()
        self.config_data = self._load_config()

    def _load_config(self):
        if not self.config_path.is_file():
            raise FileNotFoundError(f"Config file not found at {self.config_path}")
        with open(self.config_path, 'r') as f:
            return json.load(f)

    def get_value(self, key_to_find, data=None):
        """
        Recursively search for a key in a nested dictionary/list structure.
        Returns the first value found for the given key.
        """
        if data is None:
            data = self.config_data

        if isinstance(data, dict):
            if key_to_find in data:
                return data[key_to_find]
            for value in data.values():
                result = self.get_value(key_to_find, value)
                if result is not None:
                    return result
        elif isinstance(data, list):
            for item in data:
                result = self.get_value(key_to_find, item)
                if result is not None:
                    return result
        return None