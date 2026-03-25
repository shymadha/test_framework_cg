import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import paramiko
import socket
from interfaces.base_interface import TestInterface
from core.logger import setup_logger

class SSHInterface(TestInterface):

    def __init__(self, host, username, password):
        self.logger = setup_logger("SSHInterface")
        self.host = host
        self.username = username
        self.password = password
        self.client=None
        self.key_file = None
        self.port = 22
        self.timeout=10

    def connect(self):
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
        try:
            if not self.client:
                self.logger.error(f"SSH Connection failed: {e}")
                raise Exception("SSH client not connected.")

            stdin, stdout, stderr = self.client.exec_command(command)
            exit_status = stdout.channel.recv_exit_status()

            return (
                stdout.read().decode().strip(),
                stderr.read().decode().strip(),
                exit_status,
            )
        except Exception as e:
            self.logger.exception(f"Error executing command '{command}': {e}")
            raise  Exception(f"Error executing command '{command}': {e}") # Re-raise so calling code can handle it


    def close(self):
        if self.client:
            self.client.close()
            self.logger.info(f"[DISCONNECTED] {self.host}")
        




# ssh = SSHInterface("10.203.238.6","siva_tk","abc1234")
# ssh.connect()
# stdout= ssh.execute("lscpu")
# print(stdout)
# ssh.close()