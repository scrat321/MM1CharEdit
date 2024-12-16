import unittest
from unittest.mock import patch, MagicMock, mock_open

from charedit import hex_edit_prompt, edit_item, validate_value_with_options, edit_character_town, value_mappings, \
    edit_character_name, display_character_names, CHARACTER_BLOCK_SIZE


class TestCharedit(unittest.TestCase):

    def setUp(self):
        self.sample_data = bytearray(CHARACTER_BLOCK_SIZE * 18 + 18)  # Mock 18 character slots
        # Fill mock data for testing
        for i in range(6):
            start = i * CHARACTER_BLOCK_SIZE
            self.sample_data[start:start + 15] = f"Char{i + 1}".ljust(15, '\x00').encode('ascii')

    def test_display_character_names(self):
        with patch('charedit.display_list_with_headers') as mock_display:
            result = display_character_names(self.sample_data)
            mock_display.assert_called_once()
            self.assertEqual(len(result), 18)
            self.assertEqual(result[0][1], 'Char1..........')

    def test_edit_character_name_success(self):
        with patch('charedit.Utility.prompt_input', return_value="NewName"), \
                patch('charedit.Logger.display'), \
                patch('charedit.Logger.info') as mock_info:
            updated_name = edit_character_name(self.sample_data, 0)
            self.assertEqual(updated_name, "NEWNAME........")
            mock_info.assert_called_with("Character name set to: NEWNAME........")

    def test_edit_character_name_invalid_length(self):
        with patch('charedit.Utility.prompt_input', return_value="ThisNameIsTooLong"), \
                patch('charedit.Logger.error') as mock_error:
            updated_name = edit_character_name(self.sample_data, 0)
            self.assertEqual(updated_name, "Char1..........")  # Original name remains unchanged
            mock_error.assert_called_with("Name exceeds the maximum length of 15 characters.")

    def test_edit_item_with_multiple_ranges(self):
        item_map = {
            1: ("Item1", [(0, 1), (2, 3)]),  # Mock multiple ranges
            2: ("Item2", [(4, 5)])
        }
        # Set initial values for ranges
        self.sample_data[0:2] = (5).to_bytes(2, byteorder='little')
        self.sample_data[2:4] = (10).to_bytes(2, byteorder='little')

        with patch('charedit.Utility.prompt_input', side_effect=["1", "20", "x"]), \
                patch('charedit.Logger.info') as mock_info:
            edit_item(self.sample_data, item_map, "Test Item")
            # Validate that only the last range was updated
            self.assertEqual(int.from_bytes(self.sample_data[2:4], byteorder='little'), 20)
            self.assertEqual(int.from_bytes(self.sample_data[0:2], byteorder='little'), 20)
            mock_info.assert_called_with("Item1 set to: 20")

    def test_edit_item_out_of_range_with_multiple_ranges(self):
        item_map = {
            1: ("Item1", [(0, 1), (2, 3)])
        }
        # Set initial values for ranges
        self.sample_data[0:2] = (5).to_bytes(2, byteorder='little')
        self.sample_data[2:4] = (10).to_bytes(2, byteorder='little')

        with patch('charedit.Utility.prompt_input', side_effect=["1", "99999", "15", "x"]), \
                patch('charedit.Logger.error') as mock_error:
            edit_item(self.sample_data, item_map, "Test Item")
            # Validate that the invalid value does not overwrite data
            self.assertEqual(int.from_bytes(self.sample_data[2:4], byteorder='little'), 15)
            self.assertEqual(int.from_bytes(self.sample_data[0:2], byteorder='little'), 15)
            mock_error.assert_called_with("Value must be between 0 and 65535.")

    def test_validate_value_with_options(self):
        allowed_values = {1: "Option1", 2: "Option2"}
        self.assertTrue(validate_value_with_options(1, allowed_values))
        self.assertFalse(validate_value_with_options(3, allowed_values))


if __name__ == "__main__":
    unittest.main()
