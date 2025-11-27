import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


class Settings:
    """Global settings manager for the application."""

    _instance: Optional["Settings"] = None
    _config_file = Path.home() / ".quint" / "config.json"

    def __new__(cls) -> "Settings":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return

        self._settings: Dict[str, Any] = {
            "documents_path": str(Path.home() / "Documents" / "Quint"),
            "algorithm": "FSRS",
            "openai_api_key": "",
            "window_width": 1600,
            "window_height": 1200,
            "window_x": -1,
            "window_y": -1,
        }

        self._load_settings()
        self._initialized = True

    def _load_settings(self) -> None:
        """Load settings from config file."""
        if self._config_file.exists():
            try:
                with open(self._config_file, "r") as f:
                    saved_settings = json.load(f)
                    self._settings.update(saved_settings)
            except (json.JSONDecodeError, IOError):
                pass

    def _save_settings(self) -> None:
        """Save current settings to config file."""
        self._config_file.parent.mkdir(exist_ok=True)
        try:
            with open(self._config_file, "w") as f:
                json.dump(self._settings, f, indent=2)
        except IOError:
            pass

    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value."""
        return self._settings.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a setting value and save to file."""
        self._settings[key] = value
        self._save_settings()

    @property
    def documents_path(self) -> str:
        return self.get("documents_path")

    @documents_path.setter
    def documents_path(self, value: str) -> None:
        self.set("documents_path", value)

    @property
    def algorithm(self) -> str:
        return self.get("algorithm")

    @algorithm.setter
    def algorithm(self, value: str) -> None:
        self.set("algorithm", value)

    @property
    def openai_api_key(self) -> str:
        return self.get("openai_api_key", "")

    @openai_api_key.setter
    def openai_api_key(self, value: str) -> None:
        self.set("openai_api_key", value)

    @property
    def window_width(self) -> int:
        return self.get("window_width", 1600)

    @window_width.setter
    def window_width(self, value: int) -> None:
        self.set("window_width", value)

    @property
    def window_height(self) -> int:
        return self.get("window_height", 1200)

    @window_height.setter
    def window_height(self, value: int) -> None:
        self.set("window_height", value)

    @property
    def window_x(self) -> int:
        return self.get("window_x", -1)

    @window_x.setter
    def window_x(self, value: int) -> None:
        self.set("window_x", value)

    @property
    def window_y(self) -> int:
        return self.get("window_y", -1)

    @window_y.setter
    def window_y(self, value: int) -> None:
        self.set("window_y", value)


# Global settings instance
settings = Settings()

