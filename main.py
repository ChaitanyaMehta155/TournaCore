"""
TournaCore - Tournament Management System
Main Entry Point
Evaluator starts the program with:
    python main.py
"""
import sys
from ui.menu import CLIApp


def main():
    """Initializes and runs the TournaCore terminal application."""
    app = CLIApp()
    try:
        app.run()
    except (KeyboardInterrupt, EOFError):
        print("\n\nOperation cancelled by user. Exiting TournaCore. Goodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()
