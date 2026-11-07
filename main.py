#  ____      ___        __  ____   _______ _____ ____
# |  _ \    / \ \      / / | __ ) |__   __|_   _/ ___|
# | |_) |  / _ \ \ /\ / /  |  _ \    | |    | | \___ \
# |  _ <  / ___ \ V  V /   | |_) |   | |    | |  ___) |
# |_| \_\/_/   \_\_/\_/    |____/    |_|    |_| |____/
#              . bytes  |  raw.bytes  |  (c) 2026
# Developer signature: raw.bytes. Third-party rights remain with their owners.

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