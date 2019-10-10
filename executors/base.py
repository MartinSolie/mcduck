from abc import ABCMeta

class BaseExecutor(metaclass=ABCMeta):
    """ Abstract executor interface """
    def execute(self, command, parameters=None):
        """
        Initiates command execution

        :command: string, command to execute
        :parameters: tuple, params for command
        :return: result code, stdout, stderr
        """
        raise NotImplementedError