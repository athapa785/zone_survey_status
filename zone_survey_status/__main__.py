import sys
import qtmodern.styles
from qtmodern.windows import ModernWindow
from PyQt5.QtWidgets import QApplication
from .view import MainWindow


def main():
    """Entry point for the application."""
    app = QApplication(sys.argv)
    
    # Apply qtmodern light style
    qtmodern.styles.light(app)
    
    # Create the main window
    window = MainWindow()
    
    # Wrap in a modern window frame
    mw = ModernWindow(window)
    mw.show()
    
    # Start the application event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()