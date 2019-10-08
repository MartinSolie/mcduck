from abc import ABCMeta

class BaseExecutor(metaclass=ABCMeta):
    """ Abstract executor interface """
    def execute(self, command, parameters=None):
        """
        Initiates system call

        :return: result code, stdout, stderr
        """
        raise NotImplementedError