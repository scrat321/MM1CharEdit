import unittest
from unittest.mock import patch
from io import StringIO
from pathlib import Path
from utility import Utility


class TestUtility(unittest.TestCase):

    @patch('sys.stdout', new_callable=StringIO)
    def test_print_message_with_border(self, mock_stdout):
        Utility.print_message_with_border("Test Message", colors_enabled=False)
        output = mock_stdout.getvalue()
        self.assertIn("+----------------+", output)
        self.assertIn("|  Test Message  |", output)
        self.assertIn("+----------------+", output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_print_options_bar(self, mock_stdout):
        options = {"s": "Save", "q": "Quit"}
        Utility.print_options_bar(options, unsaved_changes=True)
        output = mock_stdout.getvalue()
        self.assertIn("s: Save", output)
        self.assertIn("q: Quit", output)

    @patch('builtins.input', return_value="user input")
    def test_prompt_input(self, mock_input):
        result = Utility.prompt_input("Enter something")
        self.assertEqual(result, "user input")

    @patch('builtins.input', return_value="warning input")
    def test_prompt_input_warn(self, mock_input):
        result = Utility.prompt_input_warn("Enter a warning")
        self.assertEqual(result, "warning input")

    def test_validate_path_exists(self):
        with patch.object(Path, 'exists', return_value=True):
            self.assertTrue(Utility.validate_path("/valid/path"))

    def test_validate_path_not_exists(self):
        with patch.object(Path, 'exists', return_value=False):
            self.assertFalse(Utility.validate_path("/invalid/path"))

    def test_format_allowed_values_in_columns(self):
        allowed_values = {"a": "Option A", "b": "Option B", "c": "Option C"}
        formatted = Utility.format_allowed_values_in_columns(allowed_values, columns=2)
        self.assertIn("a (Option A)", formatted)
        self.assertIn("b (Option B)", formatted)
        self.assertIn("c (Option C)", formatted)

    @patch('sys.stdout', new_callable=StringIO)
    def test_display_in_columns(self, mock_stdout):
        items = ["Item1", "Item2", "Item3", "Item4"]
        Utility.display_in_columns(items, columns=2)
        output = mock_stdout.getvalue()
        self.assertIn("Item1", output)
        self.assertIn("Item2", output)
        self.assertIn("Item3", output)
        self.assertIn("Item4", output)


if __name__ == "__main__":
    unittest.main()
