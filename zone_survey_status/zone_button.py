from PyQt5.QtWidgets import QPushButton, QSizePolicy, QStyleOptionButton, QStyle
from PyQt5.QtCore import QSize, QRectF
from PyQt5.QtGui import QColor, QFont, QPainter, QTextDocument
from .dialogs import show_state_dialog, ask_posting_changes
from datetime import datetime


# Mapping of internal state keys to display label and color
STATE_INFO = {
    "not_started":          {"label": "Survey not started",                  "color": QColor("red")},
    "in_progress":          {"label": "Survey in progress",                  "color": QColor("yellow")},
    "complete_cleared":     {"label": "Survey complete",                      "color": QColor("green")},
    "complete_not_cleared": {"label": "Survey complete -- Not cleared for entry", "color": QColor("maroon")},
}

class ZoneButton(QPushButton):
    """
    A QPushButton that represents a PPS zone and its survey state.
    Displays zone name, completion timestamp, and posting changes.
    """

    def __init__(self, zone_name, state_manager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.zone_name = zone_name
        self.state_manager = state_manager
        
        # Set size policy to expand in both directions
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Set minimum size for the button
        self.setMinimumSize(QSize(150, 100))
        
        # Create fonts for zone name (large) and other text (small)
        self.zone_name_font = QFont()
        self.zone_name_font.setPointSize(18)
        self.zone_name_font.setBold(True)
        
        self.small_font = QFont()
        self.small_font.setPointSize(12)
        
        # Connect the click event to the dialog handler
        self.clicked.connect(self.on_clicked)
        
        self.html = ""
        # Initialize appearance based on loaded state
        self.update_appearance()

    def update_appearance(self):
        """Update button color and text based on the current survey state."""
        info = self.state_manager.states.get(self.zone_name, {})
        state_key = info.get("state", "not_started")
        mapping = STATE_INFO.get(state_key, STATE_INFO["not_started"])
        color = mapping["color"]
        
        # Set background color via stylesheet
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color.name()};
                padding: 10px;
                text-align: center;
                white-space: normal;
            }}
        """)
        
        # Build HTML content with styling
        html = f"""
            <div style="text-align:center;">
                <div style="font-size:18pt; font-weight:bold;">{self.zone_name}</div>
                <div style="font-size:12pt;">{mapping['label']}</div>
        """
        
        timestamp = info.get("timestamp")
        if timestamp:
            html += f'<div style="font-size:12pt;">{timestamp}</div>'
            
        changes = info.get("changes")
        if changes:
            html += f'<div style="font-size:12pt;">{changes}</div>'
        
        html += "</div>"
        
        # Store HTML for custom painting and clear default text
        self.html = html
        super().setText("")  # Prevent default text drawing

    def on_clicked(self):
        """
        Handle user click: show state selection, update timestamp/changes,
        save to persistent storage, and refresh appearance.
        """
        current_state = self.state_manager.states[self.zone_name]["state"]
        new_state = show_state_dialog(current_state)
        if new_state is None:
            return  # User canceled the dialog
        # If survey marked complete, record timestamp and ask postings question
        timestamp = ""
        changes = ""
        if new_state in ("complete_cleared", "complete_not_cleared"):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Pass the state to the ask_posting_changes function
            changes = ask_posting_changes(new_state)
        # Update state manager
        self.state_manager.states[self.zone_name] = {
            "state": new_state,
            "timestamp": timestamp,
            "changes": changes
        }
        self.state_manager.save_states()
        # Refresh button
        self.update_appearance()

    def paintEvent(self, event):
        # Draw the button background and border
        opt = QStyleOptionButton()
        self.initStyleOption(opt)
        painter = QPainter(self)
        self.style().drawControl(QStyle.CE_PushButtonBevel, opt, painter, self)

        # Draw the HTML content centered vertically
        painter.save()
        rect = self.contentsRect()
        doc = QTextDocument(self)
        doc.setHtml(self.html)
        doc.setTextWidth(rect.width())
        
        # Calculate vertical centering
        doc_height = doc.size().height()
        button_height = rect.height()
        y_offset = max(0, (button_height - doc_height) / 2)
        
        # Translate to center vertically
        painter.translate(rect.left(), rect.top() + y_offset)
        doc.drawContents(painter, QRectF(0, 0, rect.width(), rect.height()))
        painter.restore()