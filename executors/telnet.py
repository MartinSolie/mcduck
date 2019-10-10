import telnetlib

from executors.base import BaseExecutor

class TelnetExecutor(BaseExecutor):
    DEFAULT_ENCODING = 'ascii'
    PROMPT_RE = "\s*{username}.*$"

    def __init__(self, host, user, password, port=None, ):
        port = port or telnetlib.TELNET_PORT
        self.user = user
        self.tn = telnetlib.Telnet(host)
        self.tn.write(self.user.encode(TelnetExecutor.DEFAULT_ENCODING) + b'\n')
        self.tn.read_until(b'Password: ')
        self._write_ignore_output(password + '\n')

    def execute(self, command, parameters=None):
        if parameters:
            command = command + ' ' + ' '.join(parameters)
        command = self.wrap_command(command)

        self.clean_shell_vars()
        self._write_ignore_output(command)
        result_code = self._parse_last_ret_value()
        stdout = self._parse_last_stdout()
        stderr = self._parse_last_stderr()
        self.clean_shell_vars()

        return result_code, stdout, stderr

    def wrap_command(self, command):
        """ Adds some stuff to the command
            After embedding user's command into this small script:
            `stdout` of the command will be saved into `t_std` variable
            `stderr` of the command will be saved into `t_err` variable
            return code of the command will be saved into `t_ret` variable
        """
        return (f'eval "$( ({command})'
                '2> >(t_err=$(cat); typeset -p t_err)'
                '> >(t_std=$(cat); typeset -p t_std); t_ret=$?; typeset -p t_ret )"\n')

    def clean_shell_vars(self):
        self._write_ignore_output('unset t_std t_err t_ret\n')

    def _parse_last_ret_value(self):
        return self._echo_variable('t_ret')
    def _parse_last_stdout(self):
        return self._echo_variable('t_std')

    def _parse_last_stderr(self):
        return self._echo_variable('t_err')

    def _echo_variable(self, variable):
        self.tn.write(f'echo ${variable}\n'.encode(TelnetExecutor.DEFAULT_ENCODING))
        _, matched, _ = self.tn.expect([TelnetExecutor.PROMPT_RE.format(username=self.user)
                                            .encode(TelnetExecutor.DEFAULT_ENCODING)])
        result = matched.string.decode(TelnetExecutor.DEFAULT_ENCODING)[:matched.start(0)]
        return result

    def _write_ignore_output(self, command):
        self.tn.write(command.encode(TelnetExecutor.DEFAULT_ENCODING))
        self.tn.expect([TelnetExecutor.PROMPT_RE.format(username=self.user)
                            .encode(TelnetExecutor.DEFAULT_ENCODING)])

    def __del__(self):
        self.tn.close()