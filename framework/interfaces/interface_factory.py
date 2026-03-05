import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from interfaces.ssh_interface import SSHInterface
from interfaces.serial_interface import SerialInterface

class InterfaceFactory:

    @staticmethod
    def create_interface(config):

        if  config["interface"]["type"] == "ssh":
            return SSHInterface(
                config["interface"]["host"],
                config["interface"]["username"],
                config["interface"]["password"]
            )

        elif  config["interface"]["type"] == "serial":
            return SerialInterface(
                config["interface"]["port"],
                config["interface"]["baudrate"]
            )

        else:
            raise ValueError("Unsupported interface type")