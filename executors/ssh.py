import base64
import paramiko

from socket import gaierror

from executors.base import BaseExecutor


class SSHExecutor(BaseExecutor):
    """Allows to connect to remote machine by ssh and execute command there

    Before running `execute`, to actually execute command, please run `connect`
    method to establish connection. And don't forget to `disconnect` when you
    are done. Or just use context manager with the instance.
    """

    SSH_PORT = paramiko.client.SSH_PORT
    DEFAULT_ENCODING = 'utf-8'

    def __init__(self, host, user=None, key_path=None, password=None, passphrase=None,
                 port=SSH_PORT, encoding=DEFAULT_ENCODING):
        self.host = host
        self.user = user
        self.key_path = key_path
        self.password = password
        self.passphrase = passphrase
        self.port = port

        self.encoding = encoding

        self.client = paramiko.SSHClient()
        # Will ignore Unknow host key
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def connect(self):
        try:
            self.client.connect(
                self.host,
                port=self.port,
                username=self.user,
                password=self.password,
                key_filename=self.key_path,
                passphrase=self.passphrase,
            )
        except gaierror as err:
            raise ValueError(f"Failed to connect to {self.host}:\n{err}")
        except (paramiko.ssh_exception.AuthenticationException, 
                paramiko.ssh_exception.BadAuthenticationType,
                paramiko.ssh_exception.PartialAuthentication,
                paramiko.ssh_exception.PasswordRequiredException) as err:
            raise ValueError(f"Failder to auth at {self.host}:\n{err}")


    def disconnect(self):
        self.client.close()

    def execute(self, command, parameters=None):
        """Initiates command execution

        :command: string, command to execute
        :parameters: tuple, params for command
        :return: result code, stdout, stderr
        """
        if parameters:
            command = command + ' ' + ' '.join(parameters)

        channel = self.client.get_transport().open_session()
        channel.exec_command(command)

        code = channel.recv_exit_status()
        stdout = channel.makefile().read().decode(self.encoding)
        stderr = channel.makefile_stderr().read().decode(self.encoding)

        channel.close()

        return code, stdout, stderr

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.disconnect()

    def __del__(self):
        # Just in case
        self.disconnect()