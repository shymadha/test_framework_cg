import json
from pathlib import Path
import os
import sys
import importlib
import argparse
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from framework.core.user_input_parser import ParseUserInput


class TestbedUtils:
    """
    Utility class for loading and querying the testbed configuration file.

    This class provides convenient methods to:
      - Locate and load the testbed.json file.
      - Access nested configuration values through recursive search.
      - Abstract config file handling away from other components.

    Attributes
    ----------
    config_path : pathlib.Path
        Absolute path to the testbed configuration file.
    config_data : dict
        Dictionary representation of the parsed JSON configuration.
    """

    def __init__(self, config_path=None):
        """
        Initialize the TestbedUtils instance and load the configuration.

        If no config path is provided, the method attempts to load:
            <project_root>/userinput/testbed.json

        Parameters
        ----------
        config_path : str or pathlib.Path, optional
            Path to a custom testbed JSON config file.
            Defaults to None, in which case the standard project structure
            is used to locate testbed.json.
        """
        if config_path is None:
            # Default to userinput/testbed.json relative to project root
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "userinput" / "testbed.json"
        
        self.config_path = Path(config_path).resolve()
        self.config_data = self._load_config()

    def _load_config(self):
        """
        Read and parse the JSON configuration file.

        Returns
        -------
        dict
            Parsed JSON data from the testbed configuration file.

        Raises
        ------
        FileNotFoundError
            If the config file does not exist at the specified path.
        JSONDecodeError
            If the file exists but contains invalid JSON.
        """
        if not self.config_path.is_file():
            raise FileNotFoundError(f"Config file not found at {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            return json.load(f)

    def get_value(self, key_to_find, data=None):
        """
        Recursively search for a key within a nested dictionary or list.

        This function performs a deep traversal of the configuration
        structure and returns the first matching key's value.

        Parameters
        ----------
        key_to_find : str
            The key to search for in the configuration.
        data : dict or list, optional
            Internal recursive parameter. Users should not provide this.
            If None, the search begins at the root of config_data.

        Returns
        -------
        any or None
            The value associated with the key if found, otherwise None.

        Notes
        -----
        - The search is depth‑first.
        - Stops at the first found match.
        - Works with JSON consisting of dictionaries, lists, or nested combinations.
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