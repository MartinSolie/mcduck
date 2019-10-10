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


@click.group()
def cli():
    pass


@click.command(help='Will execute COMMAND locally',
               context_settings={'ignore_unknown_options':True,})
@click.argument('command')
@click.argument('command_args', nargs=-1, type=click.UNPROCESSED)
def local(command, command_args):
    executor = LocalExecutor()
    res = json_repr(*executor.execute(command, command_args))
    print(res)


# TODO: Password requesting
# TODO: check passphrase, request passphrase
@click.command(help='Will execute COMMAND via ssh',
               context_settings={'ignore_unknown_options':True,})
@click.argument('connection_string')
@click.argument('command')
@click.argument('command_args', nargs=-1, type=click.UNPROCESSED)
@click.option('-i', '--identity', help='Full path to identity file')
@click.option('-p', '--port', type=click.INT, default=SSHExecutor.SSH_PORT,
              help=f"Port to connect. Default is {SSHExecutor.SSH_PORT}")
def ssh(connection_string, command, identity, port, command_args):
    user = password = None
    if '@' in connection_string:
        user, connection_string = connection_string.split('@')
        if ':' in user:
            user, password = user.split(':')
    # port = port or SSHExecutor.SSH_PORT

    executor = SSHExecutor(
        connection_string,
        port=port,
        user=user,
        password=password,
        key_path=identity,
    )

    res = json_repr(*executor.execute(command, command_args))

    print(res)


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
    try:
        user, host = connection_string.split('@')
    except ValueError:
        click.echo('connection_string must be in user@host format')
        return None

    executor = TelnetExecutor(host, user, password)
    res = json_repr(*executor.execute(command, parameters=command_args))
    click.echo(res)


# TODO: Don't like violation of DRY:
cli.add_command(local)
cli.add_command(ssh)
cli.add_command(telnet)

if __name__ == '__main__':
    cli()