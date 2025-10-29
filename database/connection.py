import os
import platform

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Base


class Database:
    _instance = None
    _engine = None
    _session = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _get_data_dir(self):
        """Get platform-specific data directory for the application."""
        system = platform.system()

        if system == "Linux":
            # Honor XDG_DATA_HOME if set, otherwise use ~/.local/share
            xdg_data_home = os.environ.get("XDG_DATA_HOME")
            if xdg_data_home:
                return os.path.join(xdg_data_home, "quint")
            else:
                return os.path.expanduser("~/.local/share/quint")

        elif system == "Darwin":  # macOS
            return os.path.expanduser("~/Library/Application Support/quint")

        elif system == "Windows":
            # Use LOCALAPPDATA environment variable
            local_app_data = os.environ.get("LOCALAPPDATA")
            if local_app_data:
                return os.path.join(local_app_data, "quint", "quint")
            else:
                # Fallback to user profile
                return os.path.expanduser("~/AppData/Local/quint/quint")

        else:
            # Fallback for unknown systems
            return os.path.expanduser("~/.quint")

    def _initialize(self):
        # Make sure dir exists
        db_dir = self._get_data_dir()
        if not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        db_path = os.path.join(db_dir, "flashcards.db")

        # Create engine and tables
        self._engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(self._engine)

        # Create session
        Session = sessionmaker(bind=self._engine)
        self._session = Session()

    @property
    def session(self):
        return self._session

    def close(self):
        if self._session:
            self._session.close()


# Global database instance
db = Database()

