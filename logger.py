class Logger:
    """
    A simple logging utility class for printing messages with color coding based on log levels.
    """
    COLORS = {
        "info": "\033[92m",  # Green for informational messages
        "error": "\033[91m",  # Red for error messages
        "warn": "\033[93m",  # Yellow for warnings
        "display": "\033[96m",  # Cyan for display text
        "menu": "\033[94m",  # Blue for menu options
        "invalid": "\033[90m",  # Grey for invalid data or options
        "text": "\033[97m",  # White for text
        "reset": "\033[0m",  # Reset
    }

    @staticmethod
    def log(message: str, level: str = "text") -> None:
        """
        Print a log message with the appropriate color based on the log level.

        Args:
            message (str): The message to log.
            level (str): The log level (e.g., "info", "error"). Defaults to "text".
        """
        color = Logger.COLORS.get(level, Logger.COLORS["text"])
        print(f"{color}{message}{Logger.COLORS['reset']}")

    @staticmethod
    def info(message: str) -> None:
        """
        Log an informational message.

        Args:
            message (str): The message to log.
        """
        Logger.log(message, "info")

    @staticmethod
    def error(message: str) -> None:
        """
        Log an error message.

        Args:
            message (str): The message to log.
        """
        Logger.log(message, "error")

    @staticmethod
    def warn(message: str) -> None:
        """
        Log a warning message.

        Args:
            message (str): The message to log.
        """
        Logger.log(message, "warn")

    @staticmethod
    def display(message: str) -> None:
        """
        Log a display message.

        Args:
            message (str): The message to log.
        """
        Logger.log(message, "display")

    @staticmethod
    def invalid(message: str) -> None:
        """
        Log an invalid message.

        Args:
            message (str): The message to log.
        """
        Logger.log(message, "invalid")

    @staticmethod
    def menu(message: str) -> None:
        """
        Log a menu message.

        Args:
            message (str): The message to log.
        """
        Logger.log(message, "menu")

    @staticmethod
    def text(message: str) -> None:
        """
        Log a plain text message.

        Args:
            message (str): The message to log.
        """
        Logger.log(message, "text")
