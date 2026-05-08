from abc import ABC, abstractmethod

class TestInterface(ABC):
    """
    Abstract base class defining the contract for all test interfaces.

    Any communication interface used in the test framework (e.g., UART, SSH,
    Telnet, JTAG, Serial, REST API, etc.) must inherit from this class and
    provide concrete implementations for the lifecycle methods:
      - connect()
      - execute()
      - close()

    This ensures uniformity across all interface types and allows the
    TestEngine and Platform objects to interact with interfaces in a
    consistent, predictable manner.
    """

    @abstractmethod
    def connect(self):
        """
        Establish a connection to the target or interface endpoint.

        Implementations may include:
          - Opening a serial port
          - Establishing a network socket
          - Creating an SSH session
          - Initializing a hardware interface

        Raises
        ------
        Exception
            If the connection cannot be established.
        """
        pass

    @abstractmethod
    def execute(self, command):
        """
        Execute a command or operation on the connected interface.

        Parameters
        ----------
        command : str
            The command or instruction to be executed on the interface.

        Returns
        -------
        any
            Interface‑specific response or output.

        Raises
        ------
        Exception
            If the execution fails or the interface is not connected.
        """
        pass

    @abstractmethod
    def close(self):
        """
        Close and clean up the interface connection.

        Ensures that resources such as ports, sessions, or streams are
        properly released.

        Raises
        ------
        Exception
            If closing the interface fails unexpectedly.
        """
        pass