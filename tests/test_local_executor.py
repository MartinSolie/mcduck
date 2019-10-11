import unittest

from executors.local import LocalExecutor

class TestLocalExecutor(unittest.TestCase):
    def setUp(self):
        self.executor = LocalExecutor()

    def test_ok(self):
        return_code, stdout, stderr = self.executor.execute('pwd')

        self.assertEqual(return_code, 0)
        self.assertEqual(stdout.strip(), '/app')
        self.assertEqual(stderr.strip(), '')

    def test_command_not_found(self):
        with self.assertRaises(FileNotFoundError):
            self.executor.execute('unknowncommand')

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
