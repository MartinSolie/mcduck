import telnetlib

from socket import gaierror

from executors.base import BaseExecutor

class TelnetExecutor(BaseExecutor):
    """Opens telnet connection and executes commands in remote shell

    During initialization connects to the remote host and gives it login
    credentials. After successful initialization you can call `execute` method
    to run commands in remote shell.

    To separate return code, stdout and stderr of the command, special shell
    variables are created in the remote shell and outputs are put there (see
    TelnetExecutor._wrap_command). To get output, executor runs command, and
    after completion, echoes t_std, t_err and t_err shell vars.
    """
    DEFAULT_ENCODING = 'ascii'

    def __init__(self, host, user, password, port=None, prompt=None,
                 encoding=DEFAULT_ENCODING):
        """
        :host:      - either domain name or IP addres of the server,
                      without port
        :user:      - remote account to be logged into
        :password:  - password for remote account to be logged into
        :port:      - port to connect to, if not set defaults to
                      telnetlib.TELNET_PORT
        :prompt:    - function, which must return a string, to be used as
                      regex to define borders of the call
        :encoding:  - encoding to be used to encode and decode messages
                      to/from the remote shell
        """
        if not user or not password:
            raise ValueError('Userless/passwordless logins are prohibited')

        port = port or telnetlib.TELNET_PORT
        self.prompt = prompt or self._default_get_prompt
        self.user = user
        self.encoding = encoding

        try:
            self.tn = telnetlib.Telnet(host)
        except gaierror as err:
            # get address info error, usually means we cannot resolve
            raise ValueError(f"Failed to connect to {host}:\n{err}")

        self.tn.write(self.user.encode(self.encoding) + b'\n')
        self.tn.read_until(b'Password: ')
        self.tn.write(password.encode(self.encoding) + b'\n')
        matched_index, _, _ = self.tn.expect([
            self.prompt().encode(self.encoding),
            'Login incorrect'.encode(self.encoding),
        ])
        if matched_index != 0:
            # 'Login incorrect' or other was found
            raise ValueError('Login with given credentials failed')

    def execute(self, command, parameters=None):
        """Initiates command execution

        :command: string, command to execute
        :parameters: tuple, params for command
        :return: result code, stdout, stderr
        """
        if parameters:
            command = command + ' ' + ' '.join(parameters)
        command = self._wrap_command(command)

        self._clean_shell_vars()
        # Command will not output anything, so just skip to next prompt
        self._write_ignore_output(command)
        result_code = int(self._parse_last_ret_value())
        stdout = self._parse_last_stdout()
        stderr = self._parse_last_stderr()
        self._clean_shell_vars()

        return result_code, stdout, stderr

    def _wrap_command(self, command):
        """Embedds command into expression to redirect outputs

        TL;DR
        After embedding user's command into this small script:
            - `stdout` of the command will be saved into `t_std` shell variable
            - `stderr` of the command will be saved into `t_err` shell variable
            - ret_code of the command will be saved into `t_ret` shell variable

        Dive deeper
        Some bash magic included:
        (ls)     >         >(...)
         |       |         |
        Command Redirects To process
                stdout    substitution

        Inside process substitution stuff:
        t_std=$(cat); typeset -p t_std
         |     |       |
        Sets  To the   Shows the
        var   content  attrs and
              of the   value of
              "file"   the var`

        And after all, this thing is evaluated and stdout, stderr and return
        code are saved into corresponding variables.
        """
        return (f'eval "$( ({command})'
                '2> >(t_err=$(cat); typeset -p t_err)'
                '> >(t_std=$(cat); typeset -p t_std);'
                't_ret=$?; typeset -p t_ret )"\n')

    def _clean_shell_vars(self):
        """Prepares remote shell for the next executions"""
        self._write_ignore_output('unset t_std t_err t_ret\n')

    def _parse_last_ret_value(self):
        return self._echo_variable('t_ret')

    def _parse_last_stdout(self):
        return self._echo_variable('t_std')

    def _parse_last_stderr(self):
        return self._echo_variable('t_err')

    def _echo_variable(self, variable):
        """Executes `echo ${variable}` in the remote shell and reads output"""
        self.tn.write(f'echo ${variable}\n'
            .encode(self.encoding))

        _, matched, read = self.tn.expect([
            self.prompt().encode(self.encoding)
        ])
        output = read.decode(self.encoding)
        # We don't need the next prompt in our output
        result = output[:matched.start(0)]
        return result

    def _write_ignore_output(self, command):
        """Writes command to the remote shell reads output up to the next
        prompt, ignores everything read (reading is just to move cursor)"""
        self.tn.write(command.encode(self.encoding))
        self.tn.expect([
            self.prompt().encode(self.encoding)
        ])

    def _default_get_prompt(self):
        """Used as default prompt regex

        To read outputs executor uses prompts as delimiters of the commands.
        Prompts may vary from host to host, to set needed prompt delimiter,
        please set `prompt` parameter of the initializer to lambda.
        Its result will be encoded and passed as regex to look for new prompts.
        """
        return f"\\s*{self.user}.*?\\$"

    def __del__(self):
        try:
            self.tn.close()
        except AttributeError:
            pass