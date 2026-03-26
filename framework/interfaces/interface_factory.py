import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from interfaces.ssh_interface import SSHInterface
from interfaces.serial_interface import SerialInterface
from interfaces.local_test_interface import LocalTestInterface


class InterfaceFactory:
    """
    Factory class responsible for constructing test interface objects.

    This class abstracts creation of various interface implementations such as:
      - SSH interfaces
      - Local execution interfaces
      - (extendable) Serial, Telnet, REST, etc.

    It reads interface configuration provided in the testbed JSON and returns
    the appropriate concrete TestInterface implementation instance.
    """

    @staticmethod
    def create_test_intf(intf_config):
        """
        Create a test interface object based on its configuration.

        Parameters
        ----------
        intf_config : dict
            Dictionary defining interface attributes such as:
              - type : str   (e.g., "ssh", "local")
              - host, username, password (for SSH)
              - any additional interface‑specific parameters

        Returns
        -------
        TestInterface
            A concrete instance of an interface (SSHInterface, LocalTestInterface, etc.)

        Raises
        ------
        ValueError
            If the interface type is unsupported or missing.
        """
        intf_type = intf_config.get("type")

        if intf_type == "ssh":
            return SSHInterface(
                intf_config.get("host"),
                intf_config.get("username"),
                intf_config.get("password")
            )

        elif intf_type == "local":
            return LocalTestInterface()

        else:
            raise ValueError(f"Unsupported interface: {intf_type}")