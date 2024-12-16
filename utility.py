import math
import random

from pathlib import Path
from typing import Union, Dict, List, Any

from logger import Logger


class Utility:
    """
    A utility class providing various helper functions for message formatting, input prompts, and data display.
    """

    @staticmethod
    def print_message_with_border(message: str, border_ends_char: str = "+", border_fill_char: str = "-", colors_enabled: bool = True) -> None:
        """
        Prints a message with a border, optionally with colorful text.

        Args:
            message (str): The message to print.
            border_ends_char (str): The character used for the border ends (default: "+").
            border_fill_char (str): The character used for the line fill (default: "-").
            colors_enabled (bool): If True, apply random colors to the message text.
        """
        # Define the border
        border = border_ends_char + border_fill_char * (len(message) + 4) + border_ends_char

        # Define color codes
        colors = ["\033[91m", "\033[92m", "\033[93m", "\033[94m", "\033[95m", "\033[96m", "\033[97m"]

        # Apply random colors if enabled
        if colors_enabled:
            colorful_message = "".join(random.choice(colors) + char for char in message) + "\033[0m"
        else:
            colorful_message = message

        # Print the border and message
        Logger.text(f"\n{border}")
        Logger.text(f"|  {colorful_message}  |")
        Logger.text(f"{border}")

    @staticmethod
    def print_options_bar(options: Dict[str, str], unsaved_changes: bool) -> None:
        """
        Prints a bar of options with visual highlights based on the presence of unsaved changes.

        Args:
            options (Dict[str, str]): A dictionary of option keys and their descriptions.
            unsaved_changes (bool): Flag indicating whether unsaved changes exist.
        """
        highlight_styles = {
            "default": "\033[47m\033[30m",  # Light gray background with black text
            "unsaved": "\033[47m\033[97m"  # Light gray background with white text
        }
        highlight_end = "\033[0m"  # Reset style

        formatted_options = []
        for key, value in options.items():
            style = highlight_styles["unsaved"] if key == "s" and unsaved_changes else highlight_styles["default"]
            formatted_options.append(f"{style} {key}: {value} {highlight_end}")

        print("\n" + f"{highlight_styles['default']}|{highlight_end}".join(formatted_options))

    @staticmethod
    def prompt_input(prompt: str) -> str:
        """
        Prompt the user for input, displaying the message in a menu color.

        Args:
            prompt (str): The prompt message to display.

        Returns:
            str: The user input, stripped of leading and trailing whitespace.
        """
        return input(f"{Logger.COLORS['menu']}{prompt}{Logger.COLORS['reset']}: ").strip()

    @staticmethod
    def prompt_input_warn(prompt: str) -> str:
        """
        Prompt the user for input, displaying the message in a warning color.

        Args:
            prompt (str): The prompt message to display.

        Returns:
            str: The user input, stripped of leading and trailing whitespace.
        """
        return input(f"{Logger.COLORS['warn']}{prompt}{Logger.COLORS['reset']}: ").strip()

    @staticmethod
    def validate_path(path: Union[str, Path]) -> bool:
        """
        Validate if the provided path exists.

        Args:
            path (Union[str, Path]): The file or directory path to validate.

        Returns:
            bool: True if the path exists, False otherwise.
        """
        return Path(path).exists()

    @staticmethod
    def format_allowed_values_in_columns(allowed_values: Dict[str, str], columns: int = 3) -> str:
        """
        Format a dictionary of allowed values into columns for display.

        Args:
            allowed_values (Dict[str, str]): A dictionary mapping keys to their descriptions.
            columns (int): The number of columns to format the values into (default: 3).

        Returns:
            str: Formatted string with the allowed values arranged in columns.
        """
        value_list = [f"{k} ({v})" for k, v in allowed_values.items()]

        num_rows = -(-len(value_list) // columns)
        rows = [value_list[i * num_rows:(i + 1) * num_rows] for i in range(columns)]

        max_row_length = max(len(row) for row in rows)
        for row in rows:
            while len(row) < max_row_length:
                row.append("")

        col_width = max(len(item) for item in value_list) + 2
        formatted_rows = ["".join(item.ljust(col_width) for item in row) for row in zip(*rows)]
        return "\n".join(formatted_rows)

    @staticmethod
    def display_stats_in_columns(stats_map: Dict[int, Any], data: bytes, value_mappings: Dict[str, Any],
                                 columns: int = 3) -> None:
        """
        Display statistics mapped from data in a formatted column layout.

        Args:
            stats_map (Dict[int, (str, List[Tuple[int, int]])]): Mapping of stat numbers to names and byte ranges.
            data (bytes): The data from which statistics are extracted.
            value_mappings (Dict[str, Any]): Value mappings for interpreting data.
            columns (int): Number of columns for display (default: 3).
        """
        rows = []
        for num, (stat, ranges) in stats_map.items():
            # Use the last range to determine the value
            start, end = ranges[-1]
            current_value = int.from_bytes(data[start:end + 1], byteorder='little', signed=False)

            if value_mappings.get(stat) and value_mappings.get(stat).get('Ref'):
                display_value = value_mappings.get(
                    value_mappings.get(stat).get('Ref'), {}).get(current_value, str(current_value))
            else:
                display_value = value_mappings.get(stat, {}).get(current_value, str(current_value))

            num_str = f" {num}" if num < 10 else f"{num}"
            rows.append((f"{num_str}. {stat}", f": {display_value}"))

        # Determine column widths for alignment
        stat_width = max(len(row[0]) for row in rows)
        value_width = max(len(row[1]) for row in rows)

        # Format rows for display
        formatted_rows = [f"{row[0].ljust(stat_width)}{row[1].ljust(value_width)}" for row in rows]

        # Split into columns
        num_rows = math.ceil(len(formatted_rows) / columns)
        grid = [formatted_rows[i:i + num_rows] for i in range(0, len(formatted_rows), num_rows)]

        for row_set in zip(*grid):
            Logger.text("  ".join(row for row in row_set))

        leftover_rows = len(formatted_rows) % num_rows
        if leftover_rows:
            for row in formatted_rows[-leftover_rows:]:
                Logger.text(row)

    @staticmethod
    def display_in_columns(items: List[str], columns: int = 1) -> None:
        """
        Displays a list of items in a specified number of columns.

        Args:
            items (List[str]): List of items to display.
            columns (int): Number of columns to divide the items into (default: 1).

        Raises:
            ValueError: If the number of columns is less than 1.
        """
        if columns < 1:
            raise ValueError("Number of columns must be at least 1.")

        max_length = max(len(str(item)) for item in items)
        row_format = ("{:<" + str(max_length + 2) + "}") * columns

        for i in range(0, len(items), columns):
            row_items = items[i:i + columns]
            # Format items, coloring items containing "Empty Slot" in light grey
            formatted_items = [
                f"\033[90m{item}\033[0m  " if 'Empty Slot.....' in item else item
                for item in row_items
            ]
            print(row_format.format(*formatted_items))
