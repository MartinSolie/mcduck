import base64
import paramiko

from executors.base import BaseExecutor


""" Will make system calls via ssh """
class SSHExecutor(BaseExecutor):
    SSH_PORT = paramiko.client.SSH_PORT
    DEFAULT_ENCODING = 'utf-8'

    def __init__(self, host, user=None, key_path=None, password=None, port=SSH_PORT):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # Connection will be closed only when instance is garbage-collected
        self.client.connect(
            host,
            port=port,
            username=user,
            password=password,
            key_filename=key_path,
        )

    def execute(self, command, parameters=None):
        if parameters:
            command = command + ' ' + ' '.join(parameters)

        channel = self.client.get_transport().open_session()
        channel.exec_command(command)

        code = channel.recv_exit_status()
        stdout = channel.makefile().read().decode(SSHExecutor.DEFAULT_ENCODING)
        stderr = channel.makefile_stderr().read().decode(SSHExecutor.DEFAULT_ENCODING)
        return code, stdout, stderr

    def __del__(self):
        # All channels will be closed after their client is closed
        self.client.close()