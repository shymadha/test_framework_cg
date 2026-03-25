import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import serial
from interfaces.base_interface import TestInterface

class SerialInterface(TestInterface):

    def __init__(self, config):
        self.port = config["port"]
        self.baudrate = config.get("baudrate", 9600)
        self.conn = None

    
    def connect(self):
        try:
            self.conn = serial.Serial(self.port, self.baudrate)
            self.logger.info(f"Serial connected on {self.port} @ {self.baudrate}")
        except Exception as e:
            self.logger.exception(f"Failed to open serial port {self.port}: {e}")
            raise   # rethrow so higher-level logic knows it failed

    def execute(self, command):
        try:
            if not self.conn:
                raise Exception("Serial connection not established")
            # Write command
            self.conn.write(command.encode() + b"\n")
            # Read response
            response = self.conn.readline().decode().strip()
            return response, ""

        except Exception as e:
            self.logger.exception(f"Error executing command '{command}': {e}")
            raise   # propagate upward

    def close(self):
        try:
            if self.conn:
                self.conn.close()
                self.logger.info("Serial connection closed")
        except Exception as e:
            self.logger.exception(f"Error while closing serial port: {e}")

