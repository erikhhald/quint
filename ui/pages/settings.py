from PyQt5.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
)

from ..template import GenericPage
from ..theme import COLORS, FONT_FAMILY
from settings.settings import settings


class SettingsPage(GenericPage):
    def __init__(self):
        super().__init__()

        # Settings form
        form_layout = QFormLayout()
        form_layout.setSpacing(20)

        # Documents Path setting
        self.documents_path_input = QLineEdit()
        self.documents_path_input.setText(settings.documents_path)
        self.documents_path_input.textChanged.connect(self.update_documents_path)
        self.documents_path_input.setStyleSheet(
            f"""
            QLineEdit {{
                font-family: {FONT_FAMILY};
                font-size: 16px;
                color: {COLORS['fg']};
                background-color: {COLORS['bg_hard']};
                border: 2px solid {COLORS['fg_faded']};
                border-radius: 5px;
                padding: 8px;
                min-width: 300px;
            }}
            QLineEdit:focus {{
                border-color: {COLORS['highlight']};
            }}
        """
        )

        documents_label = QLabel("Documents Path:")
        documents_label.setStyleSheet(
            f"""
            QLabel {{
                font-family: {FONT_FAMILY};
                font-size: 16px;
                color: {COLORS['fg']};
                font-weight: bold;
            }}
        """
        )

        # Create horizontal layout for path input and button
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.documents_path_input)

        # Open folder button
        open_folder_btn = QPushButton("📁")
        open_folder_btn.setFixedSize(40, 40)
        open_folder_btn.setStyleSheet(
            f"""
            QPushButton {{
                font-family: {FONT_FAMILY};
                font-size: 18px;
                color: {COLORS['fg']};
                background-color: {COLORS['bg_hard']};
                border: 2px solid {COLORS['fg_faded']};
                border-radius: 5px;
                margin-left: 5px;
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
        open_folder_btn.clicked.connect(self.open_folder_dialog)
        path_layout.addWidget(open_folder_btn)

        form_layout.addRow(documents_label, path_layout)

        # Algorithm selector
        algorithm_label = QLabel("Algorithm:")
        algorithm_label.setStyleSheet(
            f"""
            QLabel {{
                font-family: {FONT_FAMILY};
                font-size: 16px;
                color: {COLORS['fg']};
                font-weight: bold;
            }}
        """
        )

        self.algorithm_combo = QComboBox()
        self.algorithm_combo.addItems(["FSRS", "SM2"])
        self.algorithm_combo.setCurrentText(settings.algorithm)
        self.algorithm_combo.currentTextChanged.connect(self.update_algorithm)
        self.algorithm_combo.setStyleSheet(
            f"""
            QComboBox {{
                font-family: {FONT_FAMILY};
                font-size: 16px;
                color: {COLORS['fg']};
                background-color: {COLORS['bg_hard']};
                border: 2px solid {COLORS['fg_faded']};
                border-radius: 5px;
                padding: 8px;
                min-width: 120px;
            }}
            QComboBox:focus {{
                border-color: {COLORS['highlight']};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {COLORS['fg']};
                margin-right: 5px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {COLORS['bg_hard']};
                color: {COLORS['fg']};
                border: 2px solid {COLORS['fg_faded']};
                selection-background-color: {COLORS['highlight']};
                selection-color: {COLORS['bg_hard']};
            }}
        """
        )

        form_layout.addRow(algorithm_label, self.algorithm_combo)

        # OpenAI API Key setting
        api_key_label = QLabel("OpenAI API Key:")
        api_key_label.setStyleSheet(
            f"""
            QLabel {{
                font-family: {FONT_FAMILY};
                font-size: 16px;
                color: {COLORS['fg']};
                font-weight: bold;
            }}
        """
        )

        self.api_key_input = QLineEdit()
        self.api_key_input.setText(settings.openai_api_key)
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.textChanged.connect(self.update_api_key)
        self.api_key_input.setStyleSheet(
            f"""
            QLineEdit {{
                font-family: {FONT_FAMILY};
                font-size: 16px;
                color: {COLORS['fg']};
                background-color: {COLORS['bg_hard']};
                border: 2px solid {COLORS['fg_faded']};
                border-radius: 5px;
                padding: 8px;
                min-width: 300px;
            }}
            QLineEdit:focus {{
                border-color: {COLORS['highlight']};
            }}
        """
        )

        form_layout.addRow(api_key_label, self.api_key_input)

        self.add_layout(form_layout)
        self.add_stretch()

    def open_folder_dialog(self):
        """Open a file dialog to select a folder and update the path input."""
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Select Documents Folder",
            self.documents_path_input.text() or "",
            QFileDialog.ShowDirsOnly,
        )

        if folder_path:
            self.documents_path_input.setText(folder_path)

    def update_documents_path(self, path: str) -> None:
        """Update the documents path setting when the input changes."""
        settings.documents_path = path

    def update_algorithm(self, algorithm: str) -> None:
        """Update the algorithm setting when the combo box changes."""
        settings.algorithm = algorithm

    def update_api_key(self, api_key: str) -> None:
        """Update the OpenAI API key setting when the input changes."""
        settings.openai_api_key = api_key
