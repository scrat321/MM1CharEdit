import unittest
from unittest.mock import patch, mock_open
from pathlib import Path
import json
from config_operations import *


class TestConfigOperations(unittest.TestCase):

    def test_load_config_file_not_found(self):
        with patch("config_operations.Path.exists", return_value=False):
            result = load_config("config.json")
            self.assertIsNone(result)

    @patch("builtins.open", new_callable=mock_open, read_data='{"save_game_file_path": "test_path"}')
    def test_get_save_game_file_path_exists(self, mock_file):
        with patch("config_operations.Path.exists", return_value=True):
            with patch("config_operations.load_config", return_value="test_path"):
                result = get_save_game_file_path("config.json")
                self.assertEqual(result, "test_path")

    @patch("config_operations.set_save_game_file_path", return_value="new_path")
    def test_get_save_game_file_path_missing(self, mock_set_path):
        with patch("config_operations.load_config", return_value=None):
            result = get_save_game_file_path("config.json")
            self.assertEqual(result, "new_path")
            mock_set_path.assert_called_once_with("config.json")


if __name__ == "__main__":
    unittest.main()
