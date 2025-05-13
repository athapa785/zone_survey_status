import json
import os
import time
import datetime
from pathlib import Path
import shutil

class StateManager:
    """
    Manages the state of PPS zone surveys, including persistence to disk.
    """
    
    # List of PPS zones
    PPS_ZONES = [
        "Linac West", "Linac Middle", "Linac East", "BSY", 
        "BTH-W", "BTH-E", "EBD-FEE", "HX-2"
    ]
    
    def __init__(self, save_file=None):
        """
        Initialize the state manager with an optional save file path.
        If no path is provided, uses ~/.pps_zone_states.json
        """
        if save_file is None:
            self.save_file = Path.home() / ".pps_zone_states.json"
        else:
            self.save_file = Path(save_file)
            
        # Initialize with empty states
        self.states = {}
        
        # Initialize each zone with a default state
        for zone in self.PPS_ZONES:
            if zone not in self.states:
                self.states[zone] = {
                    "state": "not_started",
                    "timestamp": "",
                    "changes": ""
                }
        
        # Track the last modification time of the file
        self.last_modified_time = 0
        
        # Load saved states if they exist
        self.load_states()
        
        # Update the last modified time after loading
        self.update_last_modified_time()
    
    def load_states(self):
        """
        Load zone states from the save file if it exists.
        """
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, 'r') as f:
                    loaded_states = json.load(f)
                    # Update our states with loaded data
                    for zone, state in loaded_states.items():
                        if zone in self.states:  # Only load known zones
                            self.states[zone] = state
                # Update the last modified time after loading
                self.update_last_modified_time()
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading states: {e}")
    
    def save_states(self):
        """
        Save current zone states to the save file.
        """
        try:
            with open(self.save_file, 'w') as f:
                json.dump(self.states, f, indent=2)
            # Update the last modified time after saving
            self.update_last_modified_time()
        except IOError as e:
            print(f"Error saving states: {e}")
    
    def create_backup(self, user_name):
        """
        Create a backup of the current state file with user information.
        
        Args:
            user_name (str): Name of the user performing the reset
        """
        if not os.path.exists(self.save_file):
            return  # No file to backup
            
        # Create a backup directory if it doesn't exist
        backup_dir = Path.home() / ".pps_survey_states_backups"
        os.makedirs(backup_dir, exist_ok=True)
        
        # Generate timestamp for the backup filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"pps_survey_states_{timestamp}.json"
        backup_path = backup_dir / backup_filename
        
        try:
            # Read the current state file
            with open(self.save_file, 'r') as f:
                state_data = json.load(f)
            
            # Add metadata about the backup
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            metadata = {
                "_metadata": {
                    "reset_by": user_name,
                    "saved_on": current_time,
                    "original_file": str(self.save_file)
                }
            }
            
            # Combine metadata with state data
            backup_data = {**metadata, **state_data}
            
            # Write to backup file
            with open(backup_path, 'w') as f:
                json.dump(backup_data, f, indent=2)
                
            print(f"Backup created at: {backup_path}")
            return True
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False
    
    def reset_states(self, user_name=None):
        """
        Reset all zones to 'not started' state.
        
        Args:
            user_name (str, optional): Name of the user performing the reset
        """
        # Create a metadata dictionary if user_name is provided
        metadata = {}
        if user_name:
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            metadata = {
                "_metadata": {
                    "reset_by": user_name,
                    "reset_on": current_time
                }
            }
        
        # Reset all zones
        zone_states = {}
        for zone in self.PPS_ZONES:
            zone_states[zone] = {
                "state": "not_started",
                "timestamp": "",
                "changes": ""
            }
        
        # Combine metadata with zone states
        self.states = {**metadata, **zone_states}
        self.save_states()
    
    def update_last_modified_time(self):
        """
        Update the stored last modification time of the state file.
        """
        if os.path.exists(self.save_file):
            self.last_modified_time = os.path.getmtime(self.save_file)
    
    def check_for_file_changes(self):
        """
        Check if the state file has been modified since the last check.
        Returns True if the file has changed, False otherwise.
        """
        if not os.path.exists(self.save_file):
            return False
            
        current_mtime = os.path.getmtime(self.save_file)
        if current_mtime > self.last_modified_time:
            self.last_modified_time = current_mtime
            return True
            
        return False