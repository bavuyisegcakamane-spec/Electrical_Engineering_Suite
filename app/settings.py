"""Application-wide settings."""

from pathlib import Path


APP_NAME = "Electrical Engineering Suite"
APP_VERSION = "0.1.0"

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 650

# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Data directory
DATA_DIR = BASE_DIR / "data"

# SQLite database
DATABASE_PATH = DATA_DIR / "electrical_engineering.db"