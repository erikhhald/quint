import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Base
from .utilities import DATA_DIR

DB_DIR = DATA_DIR + "/db"


class Database:
    _instance = None
    _engine = None
    _session = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        # Make sure dir exists
        if not os.path.exists(DB_DIR):
            os.makedirs(DB_DIR, exist_ok=True)
        db_path = os.path.join(DB_DIR, "decks.db")

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
