"""Application entry point."""

import sys

from app.application import create_application, MainWindow


def main():
    """Start the application."""

    application = create_application()

    window = MainWindow()
    window.show()

    sys.exit(application.exec())


if __name__ == "__main__":
    main()