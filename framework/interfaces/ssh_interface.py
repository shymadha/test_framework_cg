import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import paramiko
import socket
from interfaces.base_interface import TestInterface
from core.logger import setup_logger


class SSHInterface(TestInterface):
    """
    Interface implementation for executing commands over SSH.

    This class provides methods to:
      - Establish an SSH connection using password or private key
      - Execute remote shell commands
      - Retrieve stdout, stderr, and exit status
      - Safely close the SSH session

    It serves as a thin wrapper around the `paramiko` library and is
    commonly used for executing commands on remote DUTs, Linux hosts,
    network devices, or test automation targets.

    Attributes
    ----------
    host : str
        Target machine hostname or IP address.
    username : str
        SSH login username.
    password : str
        SSH login password (used if private key not provided).
    key_file : str or None
        Path to a private key file for key-based authentication.
    port : int
        SSH port number (default: 22).
    timeout : int
        Connection timeout in seconds (default: 10).
    client : paramiko.SSHClient or None
        Active SSHClient instance once connected.
    logger : logging.Logger
        Logger for SSHInterface activity.
    """

    def __init__(self, host, username, password):
        """
        Initialize the SSH interface with connection parameters.

        Parameters
        ----------
        host : str
            Hostname or IP address of the target machine.
        username : str
            SSH username.
        password : str
            SSH password (used if key_file is not set).
        """
        self.logger = setup_logger("SSHInterface")
        self.host = host
        self.username = username
        self.password = password
        self.client = None
        self.key_file = None
        self.port = 22
        self.timeout = 10

    def connect(self):
        """
        Establish an SSH connection using Paramiko.

        If `key_file` is provided, authentication is performed using the
        private key. Otherwise, password authentication is used.

        Raises
        ------
        Exception
            If the SSH connection fails due to network errors or bad
            authentication credentials.
        """
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            if self.key_file:
                private_key = paramiko.RSAKey.from_private_key_file(self.key_file)
                self.client.connect(
                    hostname=self.host,
                    port=self.port,
                    username=self.username,
                    pkey=private_key,
                    timeout=self.timeout
                )
            else:
                self.client.connect(
                    hostname=self.host,
                    port=self.port,
                    username=self.username,
                    password=self.password,
                    timeout=self.timeout
                )

            self.logger.info(f"[CONNECTED] {self.host}")

        except (paramiko.SSHException, socket.error) as e:
            self.logger.error(f"SSH Connection failed: {e}")
            raise Exception(f"SSH Connection failed: {e}")

    def execute(self, command):
        """
        Execute a remote shell command on the SSH host.

        Parameters
        ----------
        command : str
            The command to run on the remote machine.

        Returns
        -------
        tuple
            (stdout, stderr, exit_status):
              stdout : str  -> Command output
              stderr : str  -> Error output
              exit_status : int -> Shell return code

        Raises
        ------
        Exception
            If the SSH client is not connected or command execution fails.
        """
        try:
            if not self.client:
                raise Exception("SSH client not connected.")

            stdin, stdout, stderr = self.client.exec_command(command)
            exit_status = stdout.channel.recv_exit_status()

            return (
                stdout.read().decode().strip(),
                stderr.read().decode().strip(),
                exit_status
            )

        except Exception as e:
            self.logger.exception(f"Error executing command '{command}': {e}")
            raise Exception(f"Error executing command '{command}': {e}")

    def close(self):
        """
        Close the SSH session and release resources.

        Safely terminates the Paramiko SSHClient connection if active.
        """
        if self.client:
            self.client.close()
            self.logger.info(f"[DISCONNECTED] {self.host}")