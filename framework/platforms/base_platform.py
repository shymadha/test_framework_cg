import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from abc import ABC, abstractmethod
from core.logger import setup_logger


class BasePlatform:
    """
    Base class representing the platform or system under test (SUT).

    This class manages:
      - Test interfaces (SSH, Serial, Local, etc.)
      - OS detection logic
      - Unified command execution wrapper
      - Resource cleanup for all registered interfaces

    Platform-specific classes (e.g., LinuxPlatform, WindowsPlatform, EmbeddedPlatform)
    should inherit from this class and extend or override functionality as needed.

    Attributes
    ----------
    logger : logging.Logger
        Logger instance for platform-related events.
    test_interfaces : dict
        Mapping of interface types to their object instances.
    os_type : str or None
        Detected operating system type ("linux", "mac", "windows"), or None if unknown.
    """

    def __init__(self):
        """
        Initialize the platform with default parameters and logger.
        """
        self.logger = setup_logger(self.__class__.__name__)
        self.test_interfaces = {}
        self.os_type = None

    def add_test_interface(self, interface_obj, interface_type):
        """
        Register a test interface with the platform.

        Parameters
        ----------
        interface_obj : TestInterface
            The interface instance (SSHInterface, SerialInterface, etc.).
        interface_type : str
            Unique key identifying the interface (e.g., "ssh", "serial").

        Raises
        ------
        ValueError
            If interface_type is missing or empty.
        """
        if not interface_type:
            raise ValueError("Interface type must be provided")
        self.test_interfaces[interface_type] = interface_obj

    def connect_test_interface(self):
        """
        Connect all registered test interfaces.

        Calls the `connect()` method on every interface in the test_interfaces dictionary.
        """
        for intf in self.test_interfaces.values():
            intf.connect()

    def exec_cmd(self, command, interface_type=None):
        """
        Execute a command using a specific interface.

        Parameters
        ----------
        command : str
            Command to be executed.
        interface_type : str, optional
            Interface identifier for executing the command.
            Must match a previously added interface.

        Returns
        -------
        tuple
            The output returned by the interface's execute() method.

        Raises
        ------
        ValueError
            If the specified interface type is not registered.
        """
        intf = None
        if interface_type:
            intf = self.test_interfaces.get(interface_type)

        if intf:
            return intf.execute(command)
        else:
            raise ValueError(f"Interface {interface_type} not found")

    def detect_os(self):
        """
        Detect the operating system of the target platform.

        The detection is performed in two stages:
          1. Try `uname` via SSH (Linux/macOS).
          2. If failed, try `ver` (Windows).

        Returns
        -------
        str
            Detected OS type: "linux", "mac", "windows", or None if unknown.
        """
        output, error, status = self.exec_cmd("uname", "ssh")
        if status == 0:
            if "Linux" in output:
                self.os_type = "linux"
            elif "Darwin" in output:
                self.os_type = "mac"
        else:
            output, error, status = self.exec_cmd("ver", "ssh")
            if "Windows" in output:
                self.os_type = "windows"

        self.logger.info(f"Detected OS: {self.os_type}")
        return self.os_type

    def get_os_type(self):
        """
        Return the detected OS type, performing OS detection if needed.

        Returns
        -------
        str
            OS type string ("linux", "mac", "windows").
        """
        if self.os_type is None:
            self.detect_os()
        return self.os_type

    def close(self):
        """
        Close all registered test interfaces.

        Safely calls the `close()` method on every interface.
        """
        for intf in self.test_interfaces.values():
            intf.close()