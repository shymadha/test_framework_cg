import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import serial
from interfaces.base_interface import TestInterface
from core.logger import setup_logger

class SerialInterface(TestInterface):

    def __init__(self, config):
                self.logger = setup_logger("SerialInterface") # added new line 
                self.port = config["port"]
                self.baudrate = config.get("baudrate", 9600)
                self.conn = None

                self.logger.info(                            # added new 
                     f"SerialInterface initialized | port={self.port}, baudrate={self.baudrate}"
                )

    def connect(self):
        try:                                                            # --> aaded new 
            self.logger.info(
                  f" opening serial connection , port = {self.port}, baudrate = {self.baudrate}")
            self.conn = serial.Serial(self.port, self.baudrate)
            self.logger.info(f"[CONNECTED] Serial port {self.port}")

        
        except Exception as e:
            self.logger.error(f"Serial connection failed: {e}")
            raise Exception(f"Serial connection failed: {e}")



    def execute(self, command):
        if not self.conn:                                            # -> aaded new 
            self.logger.error("Serial connection not established")
            raise Exception("Serial connection not established.")


        try:
            self.logger.info(f"Sending command on serial: {command}")
            self.conn.write(command.encode() + b"\n")
            response = self.conn.readline().decode().strip()
            self.logger.info(
              f"Command executed | response={response if response else 'EMPTY'}"
            )
            return response, ""
        except Exception as e:
            self.logger.error(f"Serial command execution failed: {e}")
            raise Exception(f"Serial command execution failed: {e}")

    
        # self.conn.write(command.encode() + b"\n")
        # return self.conn.readline().decode(), ""

    def close(self):
        if  self.conn:
            try:
                self.conn.close()
                self.logger.info(f"[DISCONNECTED] Serial port {self.port}")

            except Exception as e:
                self.logger.error(f"Failed to close serial connection: {e}")


