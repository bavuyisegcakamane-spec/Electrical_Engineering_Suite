"""Application entry point."""

import sys

from app.application import (
    create_application,
    MainWindow,
)

from database.database import Database


def main():
    """Start the application."""

    database = Database()

    try:
        database.initialize()

        application = create_application()

        window = MainWindow(database)

        window.show()

        exit_code = application.exec()

    finally:
        database.close()

    sys.exit(exit_code)


if __name__ == "__main__":
    main()