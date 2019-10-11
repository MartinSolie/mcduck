import unittest

from executors.ssh import SSHExecutor


class TestSSHExecutorConnection(unittest.TestCase):
    def test_ok(self):
        self.executor = SSHExecutor('127.0.0.1', user='admin',
                                    password='sIcretandsecYre')
        with self.executor:
            transport = self.executor.client.get_transport()
            self.assertTrue(transport.is_active())


    def test_connection_to_non_existent_domain(self):
        self.executor = SSHExecutor('nonexistentdomain.ua', user='admin',
                                    password='sIcretandsecYre')
        with self.assertRaises(ValueError):
            self.executor.connect()

    def test_wrong_account(self):
        self.executor = SSHExecutor('127.0.0.1', user='nonexistent',
                                    password='sIcretandsecYre')
        with self.assertRaises(ValueError):
            self.executor.connect()

    def test_wrong_password(self):
        self.executor = SSHExecutor('127.0.0.1', user='admin',
                                    password='wrongpassword')
        with self.assertRaises(ValueError):
            self.executor.connect()

    def test_empty_password(self):
        self.executor = SSHExecutor('127.0.0.1', user='admin',
                                    password='')
        with self.assertRaises(ValueError):
            self.executor.connect()

    def test_empty_user(self):
        self.executor = SSHExecutor('127.0.0.1', user='',
                                    password='sIcretandsecYre')
        with self.assertRaises(ValueError):
            self.executor.connect()

    
class TestSSHExecutor(unittest.TestCase):
    def setUp(self):
        self.executor = SSHExecutor('127.0.0.1', user='admin',
                                    password='sIcretandsecYre')

    def test_ok(self):
        with self.executor:
            return_code, stdout, stderr = self.executor.execute('pwd')
        self.assertEqual(return_code, 0)
        self.assertEqual(stdout.strip(), '/home/admin')
        self.assertEqual(stderr.strip(), '')

    def test_command_not_found(self):
        with self.executor:
            return_code, stdout, stderr = self.executor.execute('unknowncommand')

        self.assertEqual(return_code, 127)
        self.assertEqual(stdout.strip(), '')
        self.assertIn('not found', stderr)

    def test_command_failed(self):
        with self.executor:
            return_code, stdout, stderr = self.executor.execute('which')

        self.assertEqual(return_code, 1)
        self.assertEqual(stdout.strip(), '')
        self.assertEqual(stderr.strip(), '')
        pass

    def test_command_with_params(self):
        with self.executor:
            return_code, stdout, stderr = self.executor.execute(
                'ls',
                ('-a', '/etc/testing')
            )

        self.assertEqual(return_code, 0)
        self.assertIn('..', stdout)
        self.assertIn('requirements.txt', stdout)
        self.assertEqual(stderr.strip(), '')
        pass

    def test_command_without_connection(self):
        with self.assertRaises(ValueError):
            self.executor.execute('ls')
