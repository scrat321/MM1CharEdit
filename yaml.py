import ast
from typing import Any, Dict, Union, TextIO

def safe_load(stream: Union[str, TextIO]) -> Dict[str, Any]:
    """A very small YAML loader supporting the subset used in this project."""
    if hasattr(stream, "read"):
        text = stream.read()
    else:
        text = str(stream)
    data: Dict[str, Any] = {}
    current_dict: Dict[Any, Any] | None = None
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if not line.startswith(" ") and stripped.endswith(":"):
            key = stripped[:-1]
            data[key] = {}
            current_dict = data[key]
            continue
        if current_dict is None:
            continue
        if ":" not in stripped:
            continue
        key_part, value_part = stripped.split(":", 1)
        key_part = key_part.strip()
        value_part = value_part.strip()
        try:
            value = ast.literal_eval(value_part)
        except Exception:
            if value_part == "":
                value = None
            else:
                try:
                    value = int(value_part)
                except ValueError:
                    value = value_part
        try:
            key = int(key_part)
        except ValueError:
            key = key_part
        current_dict[key] = value
    return data
