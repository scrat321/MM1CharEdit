import yaml
import json

from pathlib import Path
from typing import Any, Optional

from logger import Logger
from utility import Utility


def load_byte_ranges() -> Any:
    """
    Load byte range mappings from the 'byte_ranges.yaml' file.

    Returns:
        Any: Parsed content of the YAML file.
    """
    with Path("byte_ranges.yaml").open('r') as f:
        return yaml.safe_load(f)


def load_value_mappings() -> Any:
    """
    Load value mappings from the 'value_mappings.yaml' file.

    Returns:
        Any: Parsed content of the YAML file.
    """
    with Path("value_mappings.yaml").open('r') as f:
        return yaml.safe_load(f)


def load_config(config_file: str) -> Optional[str]:
    """
    Load the configuration from the specified JSON config file.

    Args:
        config_file (str): Path to the configuration file.

    Returns:
        Optional[str]: The save game file path from the configuration, or None if not found.
    """
    config_path = Path(config_file)
    if config_path.exists():
        try:
            with config_path.open("r") as f:
                config = json.load(f)
                return config.get("save_game_file_path")
        except json.JSONDecodeError:
            Logger.error("Config file is corrupted. Resetting configuration.")
            return None
    return None


def save_config(config_file: str, save_game_file_path: str) -> None:
    """
    Save the save game file path to the specified configuration file.

    Args:
        config_file (str): Path to the configuration file.
        save_game_file_path (str): The save game file path to store.
    """
    config = {"save_game_file_path": save_game_file_path}
    with Path(config_file).open("w") as f:
        json.dump(config, f)
    Logger.info(f"Configuration saved. Current save game file path: {save_game_file_path}")


def set_save_game_file_path(config_file: str) -> str:
    """
    Prompt the user to input and set the save game file path.

    Args:
        config_file (str): Path to the configuration file.

    Returns:
        str: The new save game file path.
    """
    while True:
        new_path = Utility.prompt_input("Enter the full path to the game's save file").strip()

        # Check for blank entry
        if not new_path:
            Logger.error("Please enter a valid path.")
            continue

        # Remove surrounding quotes, if any
        new_path = new_path.strip('\'"')

        # Normalize the path to handle different separators and formats
        normalized_path = Path(new_path).resolve()

        if Utility.validate_path(normalized_path):
            save_config(config_file, str(normalized_path))
            return str(normalized_path)
        else:
            Logger.error("The file does not exist. Please enter a valid path.")


def get_save_game_file_path(config_file: str) -> str:
    """
    Retrieve the save game file path from the configuration. If not set, prompt the user to configure it.

    Args:
        config_file (str): Path to the configuration file.

    Returns:
        str: The save game file path.
    """
    save_game_file_path = load_config(config_file)
    if not save_game_file_path:
        Logger.warn("Save game file path is not configured.")
        save_game_file_path = set_save_game_file_path(config_file)
    return save_game_file_path
