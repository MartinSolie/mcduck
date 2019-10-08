import subprocess

from executors.base import BaseExecutor

class LocalExecutor(BaseExecutor):
    """ Will make system calls locally """
    def execute(self, command, parameters=None):
        parameters = parameters or []
        res = subprocess.run([command] + list(parameters), capture_output=True)
        return res.returncode, res.stdout.decode('utf-8'), res.stderr.decode('utf-8')