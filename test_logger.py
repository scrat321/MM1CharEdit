import unittest
from unittest.mock import patch
from io import StringIO

from logger import Logger


class TestLogger(unittest.TestCase):

    def setUp(self):
        self.message = "Test Message"

    @patch('sys.stdout', new_callable=StringIO)
    def test_log_info(self, mock_stdout):
        Logger.info(self.message)
        self.assertIn(f"\033[92m{self.message}\033[0m", mock_stdout.getvalue())

    @patch('sys.stdout', new_callable=StringIO)
    def test_log_error(self, mock_stdout):
        Logger.error(self.message)
        self.assertIn(f"\033[91m{self.message}\033[0m", mock_stdout.getvalue())

    @patch('sys.stdout', new_callable=StringIO)
    def test_log_warn(self, mock_stdout):
        Logger.warn(self.message)
        self.assertIn(f"\033[93m{self.message}\033[0m", mock_stdout.getvalue())

    @patch('sys.stdout', new_callable=StringIO)
    def test_log_display(self, mock_stdout):
        Logger.display(self.message)
        self.assertIn(f"\033[96m{self.message}\033[0m", mock_stdout.getvalue())

    @patch('sys.stdout', new_callable=StringIO)
    def test_log_invalid(self, mock_stdout):
        Logger.invalid(self.message)
        self.assertIn(f"\033[90m{self.message}\033[0m", mock_stdout.getvalue())

    @patch('sys.stdout', new_callable=StringIO)
    def test_log_menu(self, mock_stdout):
        Logger.menu(self.message)
        self.assertIn(f"\033[94m{self.message}\033[0m", mock_stdout.getvalue())

    @patch('sys.stdout', new_callable=StringIO)
    def test_log_text(self, mock_stdout):
        Logger.text(self.message)
        self.assertIn(f"\033[97m{self.message}\033[0m", mock_stdout.getvalue())

    @patch('sys.stdout', new_callable=StringIO)
    def test_log_default(self, mock_stdout):
        Logger.log(self.message)
        self.assertIn(f"\033[97m{self.message}\033[0m", mock_stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
