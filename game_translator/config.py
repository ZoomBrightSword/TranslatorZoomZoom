import json
import os
from pathlib import Path

# Define the application data directory
APP_NAME = "GameTranslator"
APP_DATA_DIR = Path(os.getenv("APPDATA", "")) / APP_NAME
CONFIG_FILE = APP_DATA_DIR / "config.json"

# Default configuration
DEFAULT_CONFIG = {
    "capture_area": [100, 100, 400, 200],  # x, y, width, height
    "font_size": 12,
    "last_window_positions": {
        "translation_window": [100, 100]
    }
}

class ConfigManager:
    """
    Handles loading and saving of application settings to a JSON file.
    """
    def __init__(self, config_path=CONFIG_FILE):
        """
        Initializes the ConfigManager.

        Args:
            config_path (Path): The path to the configuration file.
        """
        self.config_path = config_path
        self.config = {}
        self._load_or_create_config()

    def _load_or_create_config(self):
        """
        Loads the configuration from the file, or creates it with defaults
        if it doesn't exist.
        """
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            if self.config_path.exists():
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
            else:
                self.config = DEFAULT_CONFIG
                self.save()
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error loading config file, falling back to defaults: {e}")
            self.config = DEFAULT_CONFIG

    def get(self, key, default=None):
        """
        Retrieves a value from the configuration.

        Args:
            key (str): The configuration key.
            default: The default value to return if the key is not found.

        Returns:
            The value associated with the key, or the default value.
        """
        return self.config.get(key, default)

    def set(self, key, value):
        """
        Sets a value in the configuration. The change is not persisted until
        save() is called.

        Args:
            key (str): The configuration key.
            value: The value to set.
        """
        self.config[key] = value

    def save(self):
        """
        Saves the current configuration to the JSON file.
        """
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4)
        except IOError as e:
            print(f"Error saving config file: {e}")

# Global instance to be used across the application
config_manager = ConfigManager()