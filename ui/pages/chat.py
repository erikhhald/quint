from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from database import services
from ..components import FileSelector
from ..template import GenericPage
from ..theme import COLORS, FONT_FAMILY


class ChatPage(GenericPage):
    def __init__(self):
        super().__init__()

        # Override the back button with navigation back button and custom behavior
        self.back_btn.clicked.disconnect()  # Remove default behavior
        self.back_btn.clicked.connect(self.on_back_clicked)

        # Add card button positioned in top left area (below back button)
        self.add_card_btn = QPushButton("+ Add Card", self)
        self.add_card_btn.setFixedSize(120, 40)
        self.add_card_btn.setStyleSheet(
            f"""
            QPushButton {{
                font-family: {FONT_FAMILY};
                font-size: 36px;
                color: {COLORS['fg']};
                background-color: {COLORS['bg_hard']};
                border: 2px solid {COLORS['fg_faded']};
                border-radius: 5px;
                margin: 5px;
            }}
            QPushButton:hover {{
                color: {COLORS['highlight']};
                border-color: {COLORS['highlight']};
                background-color: {COLORS['bg_soft']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['fg_faded']};
            }}
        """
        )
        self.add_card_btn.clicked.connect(self.on_add_card_clicked)
        # Position it below the back button
        self.add_card_btn.move(10, 60)
        self.add_card_btn.raise_()  # Bring to front

        # Add spacer to push input to bottom
        self.add_stretch()

        # Chat input area
        input_layout = QHBoxLayout()

        self.chat_input = QLineEdit()
        self.chat_input.setText("> ")
        self.chat_input.setStyleSheet(
            f"""
            QLineEdit {{
                font-family: {FONT_FAMILY};
                font-size: 32px;
                color: {COLORS['fg']};
                background-color: {COLORS['bg_hard']};
                border: 1px solid {COLORS['fg_dim']};
                padding: 20px 30px;
                border-radius: 12px;
                selection-background-color: {COLORS['highlight']};
                selection-color: {COLORS['bg_hard']};
            }}
            QLineEdit:focus {{
                border: 1px solid {COLORS['highlight']};
            }}
            """
        )
        self.chat_input.returnPressed.connect(self.send_message)
        # Set cursor position after the '> '
        self.chat_input.setCursorPosition(2)

        send_btn = QPushButton("Send")
        send_btn.setStyleSheet(
            f"""
            QPushButton {{
                font-family: {FONT_FAMILY};
                font-size: 32px;
                color: {COLORS['bg_hard']};
                background-color: {COLORS['highlight']};
                border: none;
                padding: 20px 40px;
                border-radius: 12px;
                margin-left: 10px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['fg']};
            }}
            """
        )
        send_btn.clicked.connect(self.send_message)

        input_layout.addWidget(self.chat_input)
        input_layout.addWidget(send_btn)

        self.add_layout(input_layout)

    def set_deck(self, deck_name, deck_id=None):
        self.deck_name = deck_name
        self.deck_id = deck_id

    def on_back_clicked(self):
        self.parent().setCurrentIndex(1)

    def on_add_card_clicked(self):
        """Handle add card button click - show add card dialog."""
        if not hasattr(self, 'deck_id') or not self.deck_id:
            QMessageBox.warning(self, "No Deck Selected", "Please select a deck first.")
            return
        
        dialog = AddCardDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            file_path = dialog.get_file_path()
            copy_file = dialog.get_copy_option()
            
            if not file_path:
                QMessageBox.warning(self, "No File Selected", "Please select a file.")
                return
            
            try:
                # Create the card using the database service
                card = services.create_card(file_path, self.deck_id, copy_file)
                if card:
                    QMessageBox.information(
                        self, "Success", f'Card created successfully from "{file_path}"!'
                    )
                else:
                    QMessageBox.warning(
                        self, "Error", "Failed to create card. Please try again."
                    )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error creating card: {str(e)}")

    def send_message(self):
        full_text = self.chat_input.text()
        # Extract message after the '> ' prefix
        message = (
            full_text[2:].strip() if full_text.startswith("> ") else full_text.strip()
        )
        if message:
            print(f"Sending message: {message}")  # Placeholder for now
            self.chat_input.setText("> ")
            self.chat_input.setCursorPosition(2)


class AddCardDialog(QDialog):
    """Dialog for adding a new card to a deck."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Card")
        self.setModal(True)
        self.setMinimumSize(800, 400)
        self.resize(800, 400)
        
        # Set dialog styling
        self.setStyleSheet(f"background-color: {COLORS['bg_soft']};")
        
        layout = QVBoxLayout()
        
        # Title label
        title_label = QLabel("Add Card to Deck")
        title_label.setStyleSheet(
            f"""
            QLabel {{
                font-family: {FONT_FAMILY};
                font-size: 36px;
                font-weight: bold;
                color: {COLORS['fg']};
                margin-bottom: 20px;
            }}
            """
        )
        layout.addWidget(title_label)
        
        # File selector
        file_label = QLabel("Select File:")
        file_label.setStyleSheet(
            f"""
            QLabel {{
                font-family: {FONT_FAMILY};
                font-size: 36px;
                color: {COLORS['fg']};
                margin-bottom: 5px;
            }}
            """
        )
        layout.addWidget(file_label)
        
        self.file_selector = FileSelector("file", self)
        layout.addWidget(self.file_selector)
        
        # Copy checkbox
        self.copy_checkbox = QCheckBox("Copy file to managed store")
        self.copy_checkbox.setChecked(True)  # Default to copying
        self.copy_checkbox.setStyleSheet(
            f"""
            QCheckBox {{
                font-family: {FONT_FAMILY};
                font-size: 36px;
                color: {COLORS['fg']};
                margin: 10px 0;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
            }}
            QCheckBox::indicator:unchecked {{
                border: 2px solid {COLORS['fg_faded']};
                background-color: {COLORS['bg_hard']};
                border-radius: 3px;
            }}
            QCheckBox::indicator:checked {{
                border: 2px solid {COLORS['highlight']};
                background-color: {COLORS['highlight']};
                border-radius: 3px;
            }}
            """
        )
        layout.addWidget(self.copy_checkbox)
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.setStyleSheet(
            f"""
            QPushButton {{
                font-family: {FONT_FAMILY};
                font-size: 36px;
                color: {COLORS['fg']};
                background-color: {COLORS['bg_hard']};
                border: 2px solid {COLORS['fg_faded']};
                border-radius: 5px;
                padding: 8px 16px;
                margin: 5px;
            }}
            QPushButton:hover {{
                color: {COLORS['highlight']};
                border-color: {COLORS['highlight']};
                background-color: {COLORS['bg_soft']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['fg_faded']};
            }}
            """
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)

    def get_file_path(self):
        """Get the selected file path."""
        return self.file_selector.get_file_path()

    def get_copy_option(self):
        """Get whether to copy the file."""
        return self.copy_checkbox.isChecked()

