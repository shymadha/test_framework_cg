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
from core.logger import setup_logger


class ParseUserInput:
    """
    Handles parsing CLI arguments, reading test configuration files,
    constructing platform and interface objects, and providing utilities
    to extract structured data from user‑provided inputs.

    This class serves as the main entry point for:
      - Parsing JSON configuration files supplied via CLI.
      - Creating the platform object using PlatformFactory.
      - Creating test interfaces using InterfaceFactory.
      - Providing helper utilities for data extraction and validation.

    Attributes
    ----------
    logger : logging.Logger
        Logger used for reporting parsing and initialization activity.
    args : argparse.Namespace
        Parsed command‑line arguments.
    user_input : dict
        Dictionary representation of the loaded configuration file.
    platform_obj : object
        Concrete platform instance created using platform factory.
    """

    def __init__(self):
        """
        Initialize the parser, load CLI arguments, and read the configuration.

        This constructor:
          - Sets up the logger.
          - Parses command line arguments.
          - Loads and validates the JSON configuration file.

        Raises
        ------
        Exception
            If argument parsing or configuration loading fails.
        """
        self.logger = setup_logger("ParseUserInput")
        try:
            self.args = self._parse_arguments()
            self.user_input = self.parse_user_input(self.args.config)
        except Exception as e:
            self.logger.exception(f"Failed during initialization: {e}")
            raise

    def parse_user_input(self, config_file):
        """
        Load and parse the user‑provided configuration JSON file.

        Parameters
        ----------
        config_file : str
            Path to the test configuration file.

        Returns
        -------
        dict
            Parsed configuration dictionary.

        Raises
        ------
        FileNotFoundError
            If the file does not exist.
        JSONDecodeError
            If the file contains malformed JSON.
        Exception
            If any other unexpected error occurs.
        """
        try:
            with open(config_file) as f:
                self.user_input = json.load(f)
            return self.user_input
        except FileNotFoundError:
            self.logger.exception(f"Config file not found: {config_file}")
            raise
        except json.JSONDecodeError as e:
            self.logger.exception(
                f"Invalid JSON in config file {config_file}: {e}"
            )
            raise
        except Exception as e:
            self.logger.exception(f"Error reading config file: {e}")
            raise

    def __create_platform_obj(self):
        """
        Create the platform object based on the configuration.

        Extracts:
          - The 'platform' field under the first SUT section.
          - Uses PlatformFactory to instantiate the correct platform implementation.

        Returns
        -------
        object
            Instance of the constructed platform class.

        Raises
        ------
        Exception
            If platform creation fails.
        """
        try:
            platform_name = self.user_input.get("SUT", [{}])[0].get(
                "platform",
                None
            )
            platform_obj = PlatformFactory.create_platform(platform_name)
            return platform_obj
        except Exception as e:
            self.logger.exception(f"Failed to create platform object: {e}")
            raise

    def create_dev_obj(self):
        """
        Create platform and interface objects based on configuration.

        Steps:
          1. Creates the platform object.
          2. Retrieves interface configuration from the JSON.
          3. For each interface:
               - Create interface object using InterfaceFactory.
               - Register interface with the platform using add_test_interface().
          4. Calls connect_test_interface() on the platform.

        Raises
        ------
        Exception
            For any failure during device/interface creation.
        """
        try:
            self.platform_obj = self.__create_platform_obj()
            interfaces = self.user_input.get("SUT", [{}])[0].get(
                "interfaces",
                []
            )

            for intf_cfg in interfaces:
                try:
                    intf_type = intf_cfg.get("type")
                    interface_obj = InterfaceFactory.create_test_intf(
                        intf_cfg
                    )
                    self.platform_obj.add_test_interface(
                        interface_obj,
                        intf_type
                    )
                except Exception as e:
                    self.logger.exception(
                        f"Failed to create interface {intf_cfg}: {e}"
                    )
                    raise

            self.platform_obj.connect_test_interface()

        except Exception as e:
            self.logger.exception(f"Error creating device objects: {e}")
            raise

    def _parse_arguments(self):
        """
        Parse command-line arguments required for running the test.

        Returns
        -------
        argparse.Namespace
            Parsed command‑line arguments containing the config path.

        Raises
        ------
        Exception
            If argument parsing fails for any reason.
        """
        try:
            parser = argparse.ArgumentParser(description="Test Runner CLI")
            parser.add_argument(
                "--config",
                required=True,
                help="Path to configuration JSON file"
            )
            return parser.parse_args()
        except Exception as e:
            self.logger.exception(f"Argument parsing failed: {e}")
            raise

    def get_platform_obj(self):
        """
        Retrieve the platform object created during initialization.

        Returns
        -------
        object
            The instantiated platform object.
        """
        return self.platform_obj

    def parse_int_output(self, output):
        """
        Extract an integer value from the platform/interface output.

        Parameters
        ----------
        output : str or int
            The raw output from platform commands or interface operations.

        Returns
        -------
        int
            The extracted integer value.

        Raises
        ------
        ValueError
            If the output contains no digits or is of an unsupported type.
        Exception
            For any unexpected errors during parsing.
        """
        try:
            if isinstance(output, int):
                return output

            if not isinstance(output, str):
                raise ValueError(f"Unexpected type: {type(output)}")

            # Extract only the numbers from the string
            match = re.search(r'\d+', output)
            if not match:
                raise ValueError(
                    f"No integer found in output: {output!r}"
                )

            return int(match.group())

        except Exception as e:
            self.logger.exception(
                f"Error parsing integer output '{output}': {e}"
            )
            raise