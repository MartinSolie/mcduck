# McDuck

Stuff to execute commands:

- locally
- via ssh
- via telnet

### Execute commands locally

#### From code:
```py
from executors.local import LocalExecutor

executor = LocalExecutor()
return_code, stdout, stderr = executor.execute('ls', ('-a', '/etc'))
```

#### From command line:
```sh
$ python3 main.py local ls -a /etc
```

### Execute commands via ssh

#### From code
```py
from executors.ssh import SSHExecutor

executor = SSHExecutor('127.0.0.1', user='admin', password='sIcretandsecYre')
with executor:
    return_code, stdout, stderr = executor.execute('ls', ('-a', '/etc'))
```

#### From command line
```sh
$ python3 main.py ssh admin:sIcretandsecYre@127.0.0.1 ls -a /etc
```

### Execute commands via telnet

#### From code
```py
from executors.telnet import TelnetExecutor

executor = TelnetExecutor('127.0.0.1', 'admin', 'sIcretandsecYre')
return_code, stdout, stderr = executor.execute('pwd')
```

#### From command line
```sh
# Password will be prompted interactively
$ python3 main.py telnet admin@127.0.0.1 ls -a /etc
```

## Testing
Please, install docker, tests are running inside docker container

```sh
docker build -t martinsolie/mcduck-test -f .ci/self_contained_test.dockerfile .
docker run --rm martinsolie/mcduck-test
```