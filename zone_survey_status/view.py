from PyQt5.QtWidgets import QMainWindow, QWidget, QGridLayout, QPushButton, QMessageBox, QSizePolicy, QHBoxLayout, QStatusBar
from PyQt5.QtCore import QTimer, QProcess
from PyQt5.QtGui import QIcon
import os
from pathlib import Path
import subprocess
from .state_manager import StateManager
from .zone_button import ZoneButton


class MainWindow(QMainWindow):
    """
    Main window containing PPS zone buttons and a reset option.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("RPFO Survey Status")
        
        # Make the window resizable
        self.setMinimumSize(600, 400)
        self.resize(1000, 700)

        # Add a status bar purely to host the grip
        #status = QStatusBar(self)
        #status.setSizeGripEnabled(True)
        #self.setStatusBar(status)
        
        # Initialize state manager
        self.state_manager = StateManager()
        
        # Set up central widget and layout
        central = QWidget()
        self.setCentralWidget(central)
        layout = QGridLayout()
        layout.setSpacing(10)  # Add spacing between buttons
        layout.setContentsMargins(10, 10, 10, 10)  # Add margins around the grid
        central.setLayout(layout)
        # Make the grid rows and columns expand evenly
        for i in range(2):
            layout.setRowStretch(i, 1)
        layout.setRowStretch(2, 0)
        for j in range(4):
            layout.setColumnStretch(j, 1)
        # Create and place zone buttons in a 2x4 grid
        self.zone_buttons = []
        zones = self.state_manager.PPS_ZONES
        positions = [(i, j) for i in range(2) for j in range(4)]
        for (row, col), zone_name in zip(positions, zones):
            button = ZoneButton(zone_name, self.state_manager)
            layout.addWidget(button, row, col)
            self.zone_buttons.append(button)
        # Create a container for the bottom row buttons
        bottom_container = QWidget()
        bottom_layout = QHBoxLayout(bottom_container)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add a reset button
        reset_btn = QPushButton("Reset All")
        reset_btn.setMinimumHeight(40)  # Set minimum height for the reset button
        reset_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        reset_btn.clicked.connect(self.reset_all)
        bottom_layout.addWidget(reset_btn)
        
        # Add an archive button
        archives_btn = QPushButton("Archive")
        archives_btn.setMinimumHeight(40)
        archives_btn.setMaximumWidth(100)
        archives_btn.clicked.connect(self.open_archives)
        bottom_layout.addWidget(archives_btn)
        
        # Add a cool script button
        cool_btn = QPushButton("Josh's Cool Script")
        cool_btn.setMinimumHeight(40)
        cool_btn.setMinimumWidth(150)
        cool_btn.clicked.connect(self.open_coolscript)
        bottom_layout.addWidget(cool_btn)
        
        # Add the bottom container to the main layout
        layout.addWidget(bottom_container, 2, 0, 1, 4)
        
        # Set up a timer to periodically check for file changes
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.check_for_updates)
        self.refresh_timer.start(2000)  # Check every 2 seconds

    def reset_all(self):
        """
        Prompt the user to confirm, identify themselves, then reset all zones to 'Survey not started'.
        Also saves a backup of the current state with user information.
        """
        # First confirmation
        reply = QMessageBox.question(
            self, "Confirm Reset",
            "Are you sure you want to reset all PPS zones?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Ask for user identification
            from PyQt5.QtWidgets import QInputDialog
            name, ok = QInputDialog.getText(
                self,
                "User Identification",
                "Please enter your name:"
            )
            
            if ok and name.strip():
                # Create a backup with user information before resetting
                self.state_manager.create_backup(name.strip())
                
                # Reset the states
                self.state_manager.reset_states(name.strip())
                self.refresh_buttons()
            elif ok:  # User clicked OK but didn't enter a name
                QMessageBox.warning(
                    self,
                    "Missing Information",
                    "You must enter your name to proceed with the reset."
                )
    
    def refresh_buttons(self):
        """
        Update the appearance of all zone buttons.
        """
        for btn in self.zone_buttons:
            btn.update_appearance()
    
    def check_for_updates(self):
        """
        Check if the state file has been modified and refresh if needed.
        """
        if self.state_manager.check_for_file_changes():
            self.state_manager.load_states()
            self.refresh_buttons()
    
    def open_archives(self):
        """
        Open the backup files directory in the system file explorer.
        """
        # Get the backup directory path
        backup_dir = Path.home() / ".pps_survey_states_backups"
        
        # Create the directory if it doesn't exist
        os.makedirs(backup_dir, exist_ok=True)
        
        # Open the directory using the appropriate method for the OS
        try:
            if os.name == 'nt':  # Windows
                os.startfile(backup_dir)
            elif os.name == 'posix':  # macOS and Linux
                if 'darwin' in os.sys.platform:  # macOS
                    subprocess.call(['open', backup_dir])
                else:  # Linux
                    subprocess.call(['xdg-open', backup_dir])
        except Exception as e:
            QMessageBox.warning(
                self,
                "Error",
                f"Could not open archives directory:\n{str(e)}"
            )
            
            
    def open_coolscript(self):
        """
        Open Josh's cool script.
        """
        title = "Cool Script"
        bash = "cd /home/physics/joshbrn/workspace/cool_script/; python cool_script.py"
        
        subprocess.Popen(["xterm", "-T", title, "-e", bash])