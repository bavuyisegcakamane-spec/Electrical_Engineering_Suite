#  ____      ___        __  ____   _______ _____ ____
# |  _ \    / \ \      / / | __ ) |__   __|_   _/ ___|
# | |_) |  / _ \ \ /\ / /  |  _ \    | |    | | \___ \
# |  _ <  / ___ \ V  V /   | |_) |   | |    | |  ___) |
# |_| \_\/_/   \_\_/\_/    |____/    |_|    |_| |____/
#              . bytes  |  raw.bytes  |  (c) 2026
# Developer signature: raw.bytes. Third-party rights remain with their owners.

"""SQLite database management."""

import sqlite3
from pathlib import Path

from app.settings import DATABASE_PATH


class Database:
    """Manage the SQLite database connection."""

    def __init__(self, database_path: Path = DATABASE_PATH):
        self.database_path = database_path
        self.connection = None

    def initialize(self):
        """Create the database directory and initialize the database."""

        self.database_path.parent.mkdir(parents=True, exist_ok=True)

        self.connection = sqlite3.connect(self.database_path)

        # Enable foreign key support.
        self.connection.execute("PRAGMA foreign_keys = ON")

        self.create_tables()

    def create_tables(self):
        """Create all database tables from schema.sql."""

        schema_path = Path(__file__).parent / "schema.sql"

        with open(schema_path, "r", encoding="utf-8") as schema_file:
            schema = schema_file.read()

        self.connection.executescript(schema)
        self.connection.commit()

    def close(self):
        """Close the database connection."""

        if self.connection is not None:
            self.connection.close()
            self.connection = None

    def is_connected(self) -> bool:
        """Return True if the database connection is open."""

        if self.connection is None:
            return False
        try:
            self.connection.execute("SELECT 1")
            return True
        except sqlite3.ProgrammingError:
            return False

    def execute(self, query, parameters=()):
        """Execute a SQL query."""

        if self.connection is None:
            raise RuntimeError("Database has not been initialized.")

        cursor = self.connection.cursor()

        cursor.execute(query, parameters)

        self.connection.commit()

        return cursor

    def fetch_one(self, query, parameters=()):
        """Return one result from a SQL query."""

        cursor = self.execute(query, parameters)

        return cursor.fetchone()

    def fetch_all(self, query, parameters=()):
        """Return all results from a SQL query."""

        cursor = self.execute(query, parameters)

        return cursor.fetchall()