import getpass

import click
import simplejson

from executors.ssh import SSHExecutor
from executors.local import LocalExecutor
from executors.telnet import TelnetExecutor


def json_repr(code, output, err):
    return simplejson.dumps({
        'code': code,
        'stdout': output,
        'stderr': err,
    })


def parse_connection_string(connection_string):
    """ Will parse connection string into user, password and host objects """
    user = None
    password = None
    host = None

    first_col_index = connection_string.find(':')
    last_at_index = connection_string.rfind('@')

    if last_at_index == -1:
        # This means that there is no username nor password, only host
        return None, None, connection_string

    host = connection_string[last_at_index+1:]

    if first_col_index != -1:
        user = connection_string[:first_col_index]
        password = connection_string[first_col_index+1:last_at_index]
    else:
        user = connection_string[:last_at_index]

    return user, password, host


@click.group()
def cli():
    pass


@click.command(context_settings={'ignore_unknown_options':True,})
@click.argument('command')
@click.argument('command_args', nargs=-1, type=click.UNPROCESSED)
def local(command, command_args):
    """ Will execute COMMAND locally """
    executor = LocalExecutor()
    res = json_repr(*executor.execute(command, command_args))
    click.echo(res)


@click.command(context_settings={'ignore_unknown_options':True,})
@click.argument('connection_string')
@click.argument('command')
@click.argument('command_args', nargs=-1, type=click.UNPROCESSED)
@click.option('-i', '--identity', help='Full path to identity file')
@click.option('-p', '--port', type=click.INT, default=SSHExecutor.SSH_PORT,
              help='Port to connect.', show_default=True)
@click.option('--rpass', is_flag=True,
              help='If passed, will request password for connection')
@click.option('--rphrase', is_flag=True,
              help='If passed will request passphrase for identity file')
def ssh(connection_string, command, identity, port,
        rpass, rphrase, command_args):
    """Will execute COMMAND via ssh

    Please pass CONNECTION_STRING in the followin format:
    [username[:password]@]<host>

    COMMAND: command to execute

    COMMAND_ARGS: params, passed to COMMAND, please prepend them with "--"\n
    """
    user, password, host = parse_connection_string(connection_string)

    if rpass:
        password = getpass.getpass('Password: ')

    passphrase = getpass.getpass('Passphrase: ') if rphrase else None

    executor = SSHExecutor(
        host,
        port=port,
        user=user,
        password=password,
        key_path=identity,
        passphrase=passphrase,
    )

    with executor:
        res = json_repr(*executor.execute(command, command_args))

    click.echo(res)


@click.command(context_settings={'ignore_unknown_options':True,})
@click.argument('connection_string')
@click.argument('command')
@click.argument('command_args', nargs=-1, type=click.UNPROCESSED)
@click.password_option(confirmation_prompt=False, default='')
def telnet(connection_string, command, password, command_args):
    """ Will execute COMMAND via telnet

    Please pass CONNECTION_STRING in the followin format: <username>@<host>

    COMMAND: command to execute

    COMMAND_ARGS: params, passed to COMMAND, please prepend them with "--"\n
    """
    user, _, host = parse_connection_string(connection_string)

    try:
        executor = TelnetExecutor(host, user, password)
    except ValueError as err:
        click.echo(err)
        return None

    res = json_repr(*executor.execute(command, parameters=command_args))
    click.echo(res)


cli.add_command(local)
cli.add_command(ssh)
cli.add_command(telnet)

if __name__ == '__main__':
    cli()