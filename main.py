import click
import simplejson

from executors.local import LocalExecutor
from executors.ssh import SSHExecutor


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
@click.option('-i', '--identity')
@click.option('-p', '--port')
def ssh(connection_string, command, identity, port, command_args):
    user = password = None
    if '@' in connection_string:
        user, connection_string = connection_string.split('@')
        if ':' in user:
            user, password = user.split(':')
    port = port or SSHExecutor.SSH_PORT

    executor = SSHExecutor(
        connection_string,
        port=port,
        user=user,
        password=password,
        key_path=identity,
    )

    res = json_repr(*executor.execute(command, command_args))

    print(res)


@click.command(help='Will execute COMMAND via telnet')
@click.argument('command')
def telnet(command):
    print(f"Will execute {command} via telnet")


# TODO: Don't like violation of DRY:
cli.add_command(local)
cli.add_command(ssh)
cli.add_command(telnet)

if __name__ == '__main__':
    cli()