# RPFO Survey Status

A PyQt5-based desktop application for tracking and managing the survey status of PPS (Personnel Protection System) zones.

## Overview

This application provides a visual interface to monitor and update the survey status of different PPS zones. It allows users to:

- View the current status of all PPS zones at a glance
- Update the status of individual zones
- Record timestamps for completed surveys
- Document posting changes
- Reset survey status of all zones to their initial state to use it again for the next set of surveys
- Access archived survey states

## Features

- **Real-time Status Display**: Color-coded buttons show the current status of each zone
- **Status Updates**: Click on a zone to update its status
- **Automatic Timestamp Recording**: When marking a survey as complete
- **Posting Changes Documentation**: Record additional information about completed surveys
- **State Persistence**: All changes are automatically saved to disk
- **File Change Detection**: Automatically refreshes when the state file is modified externally
- **Backup System**: Creates backups before resetting all zones
- **Archive Access**: View previously saved states

## Supported Zone States

- Survey not started (red)
- Survey in progress (yellow)
- Survey complete (green)
- Survey complete -- Not cleared for entry (maroon)

## Technical Details

- Built with PyQt5 and qtmodern for a modern UI appearance
- State information is stored in JSON format
- Backups are saved with user information and timestamps
- Supports cross-platform operation (Windows, macOS, Linux)

## Installation

1. Ensure Python 3.6+ is installed
2. Install required dependencies:
   ```
   pip install PyQt5 qtmodern
   ```
3. Clone or download this repository
4. Run the application:
   ```
   python -m zone_survey_status
   ```

## File Structure

- `__main__.py`: Entry point for the application
- `state_manager.py`: Manages the state of PPS zone surveys and persistence
- `view.py`: Main window UI implementation
- `zone_button.py`: Custom button widget for zone display
- `dialogs.py`: Dialog windows for state selection and user input

## Data Storage

- Current state is stored in `~/.pps_zone_states.json`
- Backups are stored in `~/.pps_survey_states_backups/`

## License

MIT License
