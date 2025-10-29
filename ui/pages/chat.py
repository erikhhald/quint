from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit
from ..components import create_navigation_back_button
from ..theme import COLORS

class ChatPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background-color: {COLORS['bg_soft']};")

        layout = QVBoxLayout()

        # Floating back button
        back_btn = create_navigation_back_button(parent=self)
        back_btn.clicked.connect(self.on_back_clicked)

        self.title = QLabel("Chat", self)
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet(
            f"font-family: monospace; font-size: 36px; color: {COLORS['fg']}; margin-bottom: 20px;"
        )
        layout.addWidget(self.title)

        # Add spacer to push input to bottom
        layout.addStretch()

        # Chat input area
        input_layout = QHBoxLayout()

        self.chat_input = QLineEdit()
        self.chat_input.setText("> ")
        self.chat_input.setStyleSheet(
            f"""
            QLineEdit {{
                font-family: monospace;
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
                font-family: monospace;
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

        layout.addLayout(input_layout)

        self.setLayout(layout)

    def set_deck(self, deck_name, deck_id=None):
        if deck_id:
            self.title.setText(f"Chat - {deck_name} (ID: {deck_id})")
            self.deck_id = deck_id
        else:
            self.title.setText(f"Chat - {deck_name}")
        self.deck_name = deck_name

    def on_back_clicked(self):
        self.parent().setCurrentIndex(1)

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