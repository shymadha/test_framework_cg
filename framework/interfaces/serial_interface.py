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
        self.conn = serial.Serial(self.port, self.baudrate)

    def execute(self, command):
        self.conn.write(command.encode() + b"\n")
        return self.conn.readline().decode(), ""

    def close(self):
        if self.conn:
            self.conn.close()
