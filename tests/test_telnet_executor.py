import unittest

from executors.telnet import TelnetExecutor

class TestTelnetExecutorConnection(unittest.TestCase):
    def test_ok(self):
        executor = None
        try:
            executor = TelnetExecutor('127.0.0.1', 'admin', 'sIcretandsecYre')
        except ValueError as err:
            self.fail(f"Conection failed:\n{err}")

        self.assertIsInstance(executor, TelnetExecutor)
        self.assertTrue(executor.tn.get_socket())

    def test_connection_to_non_existent_domain(self):
        with self.assertRaises(ValueError):
            executor = TelnetExecutor(
                'nonexistentdomain.ua',
                'admin',
                'sIcretandsecYre'
            )

    def test_wrong_account(self):
        with self.assertRaises(ValueError):
            TelnetExecutor('127.0.0.1', 'nonexistent', 'sIcretandsecYre')

    def test_wrong_password(self):
        with self.assertRaises(ValueError):
            TelnetExecutor('127.0.0.1', 'admin', 'IncorrectPassword')

    def test_empty_password(self):
        with self.assertRaises(ValueError):
            TelnetExecutor('127.0.0.1', 'admin', '')

    def test_empty_user(self):
        with self.assertRaises(ValueError):
            TelnetExecutor('127.0.0.1', '', 'IncorrectPassword')
    
    # TODO: Add timeout proxying to TelnetExecutor
    # def test_connection_to_non_listening_server(self):
    #     executor = None
    #     try:
    #         executor = TelnetExecutor(
    #             'example.com',
    #             'admin',
    #             'sIcretandsecYre'
    #         )
    #     except ValueError as err:
    #         self.fail(f"Conection failed:\n{err}")

    #     self.assertIsInstance(executor, TelnetExecutor)
    #     self.assertTrue(executor.tn.get_socket())


class TestTelnetExecutorExecute(unittest.TestCase):
    def setUp(self):
        self.executor = TelnetExecutor('127.0.0.1', 'admin', 'sIcretandsecYre')

    def test_ok(self):
        return_code, stdout, stderr = self.executor.execute('pwd')

        self.assertEqual(return_code, 0)
        self.assertEqual(stdout.strip(), '/home/admin')
        self.assertEqual(stderr.strip(), '')

    def test_command_not_found(self):
        return_code, stdout, stderr = self.executor.execute('unknowncommand')

        self.assertEqual(return_code, 127)
        self.assertEqual(stdout.strip(), '')
        self.assertIn('not found', stderr)

    def test_command_failed(self):
        return_code, stdout, stderr = self.executor.execute('which')

        self.assertEqual(return_code, 1)
        self.assertEqual(stdout.strip(), '')
        self.assertEqual(stderr.strip(), '')

    def test_command_with_params(self):
        return_code, stdout, stderr = self.executor.execute(
            'ls',
            ('-a', '/etc/testing')
        )

        self.assertEqual(return_code, 0)
        self.assertIn('..', stdout)
        self.assertIn('requirements.txt', stdout)
        self.assertEqual(stderr.strip(), '')
