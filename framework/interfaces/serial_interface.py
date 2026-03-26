import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import serial
from interfaces.base_interface import TestInterface


class SerialInterface(TestInterface):
    """
    Concrete implementation of TestInterface for serial communication.

    This class provides methods to:
      - Establish a serial connection
      - Send and receive commands over a UART/COM port
      - Cleanly close the connection

    It acts as a wrapper around the `pyserial` library and is typically used
    for communicating with embedded devices, microcontrollers, or DUTs
    connected via serial interface.

    Attributes
    ----------
    port : str
        The serial port name (e.g., "COM3", "/dev/ttyUSB0").
    baudrate : int
        Communication speed in bits per second.
    conn : serial.Serial or None
        The underlying serial connection instance.
    """

    def __init__(self, config):
        """
        Initialize the SerialInterface with configuration parameters.

        Parameters
        ----------
        config : dict
            Configuration dictionary containing:
                - "port": str      (required)
                - "baudrate": int  (optional, defaults to 9600)
        """
        self.port = config["port"]
        self.baudrate = config.get("baudrate", 9600)
        self.conn = None

    def connect(self):
        """
        Establish a serial connection using the provided port and baudrate.

        Raises
        ------
        Exception
            If the serial port cannot be opened, or hardware initialization fails.
        """
        try:
            self.conn = serial.Serial(self.port, self.baudrate)
            self.logger.info(f"Serial connected on {self.port} @ {self.baudrate}")
        except Exception as e:
            self.logger.exception(f"Failed to open serial port {self.port}: {e}")
            raise

    def execute(self, command):
        """
        Send a command through the serial interface and read the response.

        Parameters
        ----------
        command : str
            The command string to send to the serial device.

        Returns
        -------
        tuple
            (response, error_message)
            response : str
                The line returned by the device.
            error_message : str
                Empty string on success, or an error message if failure occurs.

        Raises
        ------
        Exception
            If the serial connection is not established or I/O fails.
        """
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
            raise

    def close(self):
        """
        Close the serial connection.

        Ensures the port is properly released and logs any errors that occur.

        Raises
        ------
        Exception
            If closing the connection encounters an unexpected failure.
        """
        try:
            if self.conn:
                self.conn.close()
                self.logger.info("Serial connection closed")
        except Exception as e:
            self.logger.exception(f"Error while closing serial port: {e}")