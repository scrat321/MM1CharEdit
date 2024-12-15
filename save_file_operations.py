from pathlib import Path

from logger import Logger


def get_character_count(file_path: str, block_size: int) -> int:
    """
    Determine the number of characters in the file based on block size.

    Args:
        file_path (str): Path to the file.
        block_size (int): The size of each character block in bytes.

    Returns:
        int: Number of character blocks in the file.
    """
    try:
        file_size = Path(file_path).stat().st_size
        character_count = file_size // block_size
        Logger.info(f"File size: {file_size} bytes, {character_count} characters slots available.")
        return character_count
    except FileNotFoundError:
        Logger.error(f"File not found: {file_path}")
        return 0


def validate_file(data: bytes, block_size: int) -> bool:
    """
    Validate if the file meets the required size constraints.

    Args:
        data (bytes): The file data to validate.
        block_size (int): The size of each character block in bytes.

    Returns:
        bool: True if the file is valid, raises ValueError otherwise.

    Raises:
        ValueError: If the file is too small or does not meet the required constraints.
    """
    # Ensure the file is large enough
    if len(data) < block_size:
        raise ValueError("File does not appear to be valid: too small for the required block size.")

    # Ensure the file has at least 18 bytes more than the last block
    if len(data) < block_size + 18:
        raise ValueError("File does not have the required extra 18 bytes beyond the last block.")

    # If both checks pass
    return True
