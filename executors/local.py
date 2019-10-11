import subprocess

from executors.base import BaseExecutor

class LocalExecutor(BaseExecutor):
    """Creates subprocess and executes command locally"""
    DEFAULT_ENCODING = 'utf-8'

    def __init__(self, encoding=DEFAULT_ENCODING):
        self.encoding = encoding

    def execute(self, command, parameters=None):
        """Initiates command execution

        :command: string, command to execute
        :parameters: tuple, params for command
        :return: result code, stdout, stderr
        """
        if parameters:
            command = [command] + list(parameters)

        res = subprocess.run(command, capture_output=True)
        return (res.returncode,
                res.stdout.decode(self.encoding),
                res.stderr.decode(self.encoding))