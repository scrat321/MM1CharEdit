import random

from save_file_operations import *
from config_operations import *

CHARACTER_BLOCK_SIZE = 127  # Each character block is 127 bytes
CONFIG_FILE = "config.json"

unsaved_changes = False  # Flag to track unsaved changes

# Load mappings for text-based fields
value_mappings = load_value_mappings()


def display_list_with_headers(header: str, items: list, formatter: callable = lambda x: x, columns: int = 1) -> None:
    """
    Displays a list of items with a header and specified formatting.

    Args:
        header: Header text to display above the list.
        items: List of items to display.
        formatter: Function to format each item.
        columns: Number of columns to display.
    """
    Logger.display(f"\n{header}")
    formatted_items = [formatter(item) for item in items]
    Utility.display_in_columns(formatted_items, columns)


def display_character_names(data: bytearray, max_characters: int = 18) -> list:
    """
    Displays character names from save data.

    Args:
        data: Byte array of save data.
        max_characters: Maximum number of characters to display.

    Returns:
        List of character names with their slot numbers.
    """
    character_names = []
    for i in range(max_characters):
        start = i * CHARACTER_BLOCK_SIZE
        end = start + 15  # Character name occupies the first 15 bytes
        name = data[start:end].decode('ascii', errors='ignore').replace('\x00', '.').strip()

        # If the name is empty, mark it as "Empty Slot....."
        if not name or name == '.' * 15:
            character_names.append((i + 1, 'Empty Slot.....'))
        else:
            character_names.append((i + 1, name))

    display_list_with_headers("Slot  Character", character_names,
                              formatter=lambda item: f"{item[0]:>3}. {item[1]}",
                              columns=3)
    return character_names


def edit_character_name(data: bytearray, char_start: int) -> str:
    """
    Edits the name of a character in the save data.

    Args:
        data: Byte array of save data.
        char_start: Starting index of the character's data block.

    Returns:
        The updated character name.
    """
    global unsaved_changes
    name_start = char_start
    name_end = name_start + 15  # Name occupies the first 15 bytes of the character block

    # Retrieve the current name
    current_name = data[name_start:name_end].decode('ascii', errors='ignore').replace('\x00', '.').strip()
    Logger.display(f"Current character name: {current_name}")

    # Prompt the user for a new name
    new_name = Utility.prompt_input(
        "Enter new character name (max 15 characters)").strip().upper()

    # If nothing was entered, keep the current name
    if not new_name:
        Logger.info("Character name unchanged.")
        return current_name

    # Validate new name length
    if len(new_name) > 15:
        Logger.error("Name exceeds the maximum length of 15 characters.")
        return current_name

    # Update name with padding if necessary
    padded_name = new_name.encode('ascii').ljust(15, b'\x00')
    data[name_start:name_end] = padded_name

    padded_display_name = padded_name.decode('ascii', errors='ignore').replace('\x00', '.')
    unsaved_changes = True  # Mark changes
    Logger.info(f"Character name set to: {padded_display_name}")

    return padded_display_name


def edit_character_town(data: bytearray, slot_number: int) -> None:
    """
    Edits the town value for a character in the save data.

    Args:
        data: Byte array of save data.
        slot_number: Character slot number.
    """
    global unsaved_changes
    town_byte = slot_number + 2285  # Byte range for the town is slot_number + 2285

    # Map town numbers to town names from value_mappings
    allowed_towns = value_mappings.get('Town', {})
    if not allowed_towns:
        Logger.error("Town mappings not found in value_mappings.")
        return

    Logger.text("Allowed values:")
    Logger.text(Utility.format_allowed_values_in_columns(allowed_towns, columns=3))

    # Retrieve the current town value
    current_town = data[town_byte]
    Logger.display(f"Current value of town: {current_town}")

    while True:
        # Prompt the user for a new town
        new_town = Utility.prompt_input("Enter new value for town").strip()
        try:
            new_town = int(new_town)
            if not validate_value_with_options(new_town, allowed_towns):
                continue

            # Update the town byte
            data[town_byte] = new_town
            unsaved_changes = True  # Mark changes
            Logger.info(f"Town set to: {allowed_towns[new_town]}")
            break
        except ValueError:
            Logger.error("Please enter a valid number.")


def validate_value_with_options(new_value: int, allowed_values: dict) -> bool:
    """
    Validates a value against allowed options.

    Args:
        new_value: Value to validate.
        allowed_values: Dictionary of allowed values.

    Returns:
        True if the value is valid, False otherwise.
    """
    if allowed_values and new_value not in allowed_values:
        Logger.error("Value must be one of the available options.")
        return False
    return True


def edit_item(data: bytearray, item_map: dict, item_type: str, columns: int = 3) -> None:
    """
    Edits an item value in the save data.

    Args:
        data: Byte array of save data.
        item_map: Mapping of item numbers to their names and byte ranges.
        item_type: Type of items to edit (e.g., "Core Stats").
        columns: Number of columns to display.
    """
    global unsaved_changes
    while True:
        Utility.print_message_with_border(f"{item_type}", colors_enabled=False)
        Utility.display_stats_in_columns(item_map, data, value_mappings, columns)

        Utility.print_options_bar({"x": "Return"}, unsaved_changes)
        item_choice = Utility.prompt_input(
            f"Enter the number of the {item_type.lower()} to edit, or 'x' to return").strip().lower()
        if item_choice == 'x':
            break

        try:
            item_choice = int(item_choice)
            if item_choice in item_map:
                item_name, (start, end) = item_map[item_choice]

                # Show allowed values if available
                allowed_values = value_mappings.get(item_name)
                if allowed_values:
                    if allowed_values.get('Ref'):
                        allowed_values = value_mappings.get(allowed_values.get('Ref'))

                    Logger.text("Allowed values:")
                    Logger.text(Utility.format_allowed_values_in_columns(allowed_values, columns=4))

                while True:
                    current_value = int.from_bytes(data[start:end + 1], byteorder='little', signed=False)
                    Logger.display(f"Current value of {item_name}: {current_value}")

                    new_value = Utility.prompt_input(f"Enter new value for {item_name}").strip()
                    try:
                        new_value = int(new_value)
                        max_value = (2 ** (8 * (end - start + 1))) - 1
                        if not (0 <= new_value <= max_value):
                            Logger.error(f"Value must be between 0 and {max_value}.")
                            continue

                        if not validate_value_with_options(new_value, allowed_values):
                            continue

                        data[start:end + 1] = new_value.to_bytes(end - start + 1, byteorder='little', signed=False)
                        unsaved_changes = True
                        if allowed_values:
                            Logger.info(f"{item_name} set to: {allowed_values[new_value]}")
                        else:
                            Logger.info(f"{item_name} set to: {new_value}")
                        break
                    except ValueError:
                        Logger.error("Please enter a valid integer.")
            else:
                Logger.error("Please select a valid item number.")
        except ValueError:
            Logger.error("Please enter a valid number or command.")


def edit_core_stats(data: bytearray, core_stats: dict) -> None:
    """
    Edits the core stats of a character.

    Args:
        data: Byte array of save data.
        core_stats: Mapping of core stats to their byte ranges.
    """
    edit_item(data, core_stats, "Core Stats")


def edit_equipped_items(data: bytearray, equipped_items: dict) -> None:
    """
    Edits the equipped items of a character.

    Args:
        data: Byte array of save data.
        equipped_items: Mapping of equipped items to their byte ranges.
    """
    edit_item(data, equipped_items, "Equipped Items", 1)


def edit_backpack_items(data: bytearray, backpack_items: dict) -> None:
    """
    Edits the backpack items of a character.

    Args:
        data: Byte array of save data.
        backpack_items: Mapping of backpack items to their byte ranges.
    """
    edit_item(data, backpack_items, "Backpack Items", 1)


def hex_edit_prompt(file_path: str, output_file: str = None) -> None:
    """
    Main editing prompt for characters in the save file.

    Args:
        file_path: Path to the save file.
        output_file: Path to save the edited file (defaults to input file).
    """
    global unsaved_changes
    try:
        # Read the game save file as binary
        with open(file_path, 'rb') as f:
            data = bytearray(f.read())
        validate_file(data, CHARACTER_BLOCK_SIZE)

        # Validate at least one character slot available in file
        character_count = get_character_count(file_path, CHARACTER_BLOCK_SIZE)
        if character_count < 1:
            Logger.error("No character data found in the file.")
            return

        # Load the byte ranges from the external YAML config file
        byte_ranges = load_byte_ranges()
        core_stats_map = {int(k): (v[0], tuple(v[1])) for k, v in byte_ranges['core_stats_map'].items()}
        equipped_items_map = {int(k): (v[0], tuple(v[1])) for k, v in byte_ranges['equipped_items_map'].items()}
        backpack_items_map = {int(k): (v[0], tuple(v[1])) for k, v in byte_ranges['backpack_items_map'].items()}

        # Main menu loop
        while True:
            # Display character names
            character_names = display_character_names(data, max_characters=character_count)
            save_marker = "*" if unsaved_changes else ""
            # Highlighted bottom bar with options
            Utility.print_options_bar({"s": f"Save Changes {save_marker}", "x": "Exit"}, unsaved_changes)

            # Top-level menu choice
            top_choice = Utility.prompt_input(
                "Select a character slot to edit, 's' to save, or 'x' to exit").strip().lower()
            if top_choice == 'x':
                if unsaved_changes:
                    confirm_exit = Utility.prompt_input_warn(
                        "You have unsaved changes. Are you sure you want to exit? (y/n)").strip().lower()
                    if confirm_exit != 'y':
                        continue
                Logger.text("Goodbye!")
                return
            elif top_choice == 's':
                if unsaved_changes:
                    if output_file is None:
                        output_file = file_path
                    with open(output_file, 'wb') as f:
                        f.write(data)
                    Logger.info("Changes saved successfully.")
                    unsaved_changes = False
                    continue
                else:
                    Logger.warn("No changes to save.")
                    continue
            try:
                char_choice = int(top_choice)
                if 1 <= char_choice <= len(character_names):
                    # Check if the selected character slot is empty
                    char_start = (char_choice - 1) * CHARACTER_BLOCK_SIZE
                    char_name = character_names[char_choice - 1][1]
                    if char_name == "Empty Slot.....":
                        Logger.error("Selected character slot is empty. Please choose a valid character.")
                        continue

                    # Adjust each map to the character's offset
                    core_stats = {num: (name, (start + char_start, end + char_start))
                                  for num, (name, (start, end)) in core_stats_map.items()}
                    equipped_items = {num: (name, (start + char_start, end + char_start))
                                      for num, (name, (start, end)) in equipped_items_map.items()}
                    backpack_items = {num: (name, (start + char_start, end + char_start))
                                      for num, (name, (start, end)) in backpack_items_map.items()}

                    while True:
                        Logger.display(f"\nEditing {char_name}")
                        Logger.text("1. Edit Name")
                        Logger.text("2. Edit Town")
                        Logger.text("3. Edit Core Stats")
                        Logger.text("4. Edit Equipped Items")
                        Logger.text("5. Edit Backpack Items")
                        Logger.text("6. Display Character Data")
                        # Highlighted bottom bar with options
                        Utility.print_options_bar({"x": "Return"}, unsaved_changes)

                        option = Utility.prompt_input("Select a menu option, or 'x' to return").strip().lower()
                        if option == 'x':
                            break
                        elif option == '1':
                            char_name = edit_character_name(data, char_start)
                        elif option == '2':
                            edit_character_town(data, char_choice)
                        elif option == '3':
                            edit_core_stats(data, core_stats)
                        elif option == '4':
                            edit_equipped_items(data, equipped_items)
                        elif option == '5':
                            edit_backpack_items(data, backpack_items)
                        elif option == '6':
                            Logger.text(f"\nName: {char_name}")
                            current_town = value_mappings.get('Town', {}).get(
                                data[char_choice + 2285], "Unknown")
                            Logger.text(f"Town: {current_town}")
                            Utility.print_message_with_border("Core Stats:", colors_enabled=False)
                            Utility.display_stats_in_columns(core_stats, data, value_mappings, columns=3)
                            Utility.print_message_with_border("Equipped Items:", colors_enabled=False)
                            Utility.display_stats_in_columns(equipped_items, data, value_mappings, columns=1)
                            Utility.print_message_with_border("Backpack Items:", colors_enabled=False)
                            Utility.display_stats_in_columns(backpack_items, data, value_mappings, columns=1)
                        else:
                            Logger.error("Please enter a valid number or command.")
                else:
                    Logger.error("Invalid slot number.")
            except ValueError:
                Logger.error("Please enter a valid number or command.")

    except Exception as e:
        Logger.error(f"An error occurred: {e}")


def print_welcome_message() -> None:
    """
    Prints the welcome message for the editor.
    """
    message = "Welcome to the Might & Magic - Book 1 Character Editor!"
    Utility.print_message_with_border(message)


def main() -> None:
    """
    Entry point for the editor.
    """
    # Display a welcome message
    print_welcome_message()

    # Get the current save game file path
    save_game_file_path = get_save_game_file_path(CONFIG_FILE)
    Logger.display(f"Current save game file path: {save_game_file_path}")

    # Prompt user to change the file path if desired
    change_path = Utility.prompt_input("Would you like to change the file path? (y/n)").strip().lower()
    if change_path == 'y':
        save_game_file_path = set_save_game_file_path(CONFIG_FILE)

    # Warn the user to create a backup before proceeding
    Logger.warn("*** Warning: Before making any changes, ensure you have created a backup copy of your save file. ***")

    # Proceed with editing
    output_file = save_game_file_path
    hex_edit_prompt(save_game_file_path, output_file)


if __name__ == "__main__":
    main()
