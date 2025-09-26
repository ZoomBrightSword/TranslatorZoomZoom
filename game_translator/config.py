import json
from pathlib import Path
from utils.logger import log, APP_DATA_DIR

# The config file path is derived from the AppData path defined in the logger
CONFIG_FILE = APP_DATA_DIR / "config.json"

# Default configuration
DEFAULT_CONFIG = {
    "capture_area": [100, 100, 400, 200],  # x, y, width, height
    "font_size": 12,
    "ocr_quality": "speed",  # Options: "speed", "quality"
    "translation_backend": "local", # Options: "local", "api"
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
                    log.info("Configuration loaded successfully.")
            else:
                log.info("No config file found. Creating one with default settings.")
                self.config = DEFAULT_CONFIG
                self.save()
        except (IOError, json.JSONDecodeError) as e:
            log.error(f"Error loading config file, falling back to defaults: {e}")
            self.config = DEFAULT_CONFIG

    def get(self, key, default=None):
        """
        Retrieves a value from the configuration.
        """
        return self.config.get(key, default)

    def set(self, key, value):
        """
        Sets a value in the configuration. The change is not persisted until
        save() is called.
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
            log.error(f"Error saving config file: {e}")

# Global instance to be used across the application
config_manager = ConfigManager()