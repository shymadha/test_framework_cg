import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from interfaces.ssh_interface import SSHInterface
from interfaces.serial_interface import SerialInterface

class InterfaceFactory:

    @staticmethod
    def create_interface(config):

        if  config["SUT"][0]["interface"]["type"] == "ssh":
            return SSHInterface(
                config["SUT"][0]["interface"]["host"],
                config["SUT"][0]["interface"]["username"],
                config["SUT"][0]["interface"]["password"]
            )

        elif  config["SUT"][0]["interface"]["type"] == "serial":
            return SerialInterface(
                config["SUT"][0]["interface"]["port"],
                config["SUT"][0]["interface"]["baudrate"]
            )

        else:
            raise ValueError("Unsupported interface type")