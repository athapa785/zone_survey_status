from PyQt5.QtWidgets import (QDialog, QRadioButton, QVBoxLayout, QLabel, 
                             QDialogButtonBox, QInputDialog, QMessageBox)


def show_state_dialog(current_state):
    """
    Show a dialog for selecting the survey state.
    Returns the selected state key or None if canceled.
    """
    dialog = QDialog()
    dialog.setWindowTitle("Select Survey State")
    layout = QVBoxLayout()
    
    # Add a label with instructions
    layout.addWidget(QLabel("Select the current survey state:"))
    
    # Create radio buttons for each state
    states = {
        "not_started": "Survey not started",
        "in_progress": "Survey in progress",
        "complete_cleared": "Survey complete",
        "complete_not_cleared": "Survey complete \n -- Not cleared for entry"
    }
    
    radio_buttons = {}
    for state_key, state_label in states.items():
        radio = QRadioButton(state_label)
        radio_buttons[state_key] = radio
        layout.addWidget(radio)
        # Select the current state
        if state_key == current_state:
            radio.setChecked(True)
    
    # Add OK/Cancel buttons
    button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
    button_box.accepted.connect(dialog.accept)
    button_box.rejected.connect(dialog.reject)
    layout.addWidget(button_box)
    
    dialog.setLayout(layout)
    
    # Execute the dialog
    result = dialog.exec_()
    if result == QDialog.Accepted:
        # Find which radio button is checked
        for state_key, radio in radio_buttons.items():
            if radio.isChecked():
                return state_key
    return None


def ask_posting_changes(state=None):
    """
    Show a dialog to ask for posting changes.
    If state is 'complete_not_cleared', directly ask what changed.
    Otherwise, first ask if there were any posting changes.
    Returns the entered text or "No changes to postings" if "No" is selected.
    """
    # For 'complete_not_cleared' state, directly ask what changed
    if state == "complete_not_cleared":
        text, ok = QInputDialog.getText(
            None, 
            "Entry Not Cleared",
            "Enter what prevented entry clearance:"
        )
        
        if ok and text:
            return text
        return "Entry not cleared - no details provided"
    
    # For other states, first ask if there were any changes
    result = QMessageBox.question(
        None, 
        "Posting Changes",
        "Were there any posting changes?",
        QMessageBox.Yes | QMessageBox.No
    )
    
    if result == QMessageBox.Yes:
        text, ok = QInputDialog.getText(
            None, 
            "Posting Changes",
            "Enter what changed:"
        )
        
        if ok and text:
            return text
        return "Changes noted but no details provided"
    
    return "No changes to postings"