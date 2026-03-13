import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from interfaces.ssh_interface import SSHInterface
from interfaces.serial_interface import SerialInterface

class InterfaceFactory:

    @staticmethod
    def create_interface(config):

        
        try:
            Interface_type = config["interface"]["type"]       #added  line

            if  config["interface"]["type"] == "ssh":
                InterfaceFactory.logger.info("Creating SSH Interface")  # added line
                return SSHInterface(
                    config["interface"]["host"],
                    config["interface"]["username"],
                    config["interface"]["password"]
                )

            elif  config["interface"]["type"] == "serial":
                InterfaceFactory.looger.info("Creating Serial Interface")  # added line
                return SerialInterface(
                    config["interface"]["port"],
                    config["interface"]["baudrate"]
                )

            else:
                raise ValueError("Unsupported interface type")
            
        except Exception as e:                                               # added line 
            InterfaceFactory.logger.error(f"Interface creation failed: {e}")