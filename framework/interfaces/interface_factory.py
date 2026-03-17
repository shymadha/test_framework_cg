import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from interfaces.ssh_interface import SSHInterface
from interfaces.serial_interface import SerialInterface
from interfaces.local_test_interface import LocalTestInterface

class InterfaceFactory:

    @staticmethod
    def create_test_intf(intf_config):
              
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

        
        