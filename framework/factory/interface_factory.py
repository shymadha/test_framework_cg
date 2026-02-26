import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from interfaces.ssh_interface import SSHInterface
from interfaces.serial_interface import SerialInterface

class InterfaceFactory:

    @staticmethod
    def create_interface(config):

        if config["type"] == "ssh":
            return SSHInterface(
                config["host"],
                config["username"],
                config["password"]
            )

        elif config["type"] == "serial":
            return SerialInterface(
                config["port"],
                config["baudrate"]
            )

        else:
            raise ValueError("Unsupported interface type")