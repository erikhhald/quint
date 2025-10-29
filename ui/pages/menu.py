from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from ..components import create_colored_icon
from ..theme import COLORS

with open("resources/logo.txt", "r") as f:
    LOGO_CONTENT = f.read()


class MenuPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background-color: {COLORS['bg_soft']};")

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        label = QLabel(LOGO_CONTENT, self)
        label.setAlignment(Qt.AlignLeft)
        label.setStyleSheet(
            f"font-family: monospace; font-size: 30px; color: {COLORS['fg']};"
        )

        layout.addWidget(label)

        def create_menu_button(text, icon_path, click_handler):
            btn = QPushButton(f"  {text}", self)  # Add spaces for icon-text spacing
            btn.setIcon(create_colored_icon(icon_path, COLORS['highlight'], 24))
            btn.setStyleSheet(
                f"""
                QPushButton {{
                    font-family: monospace; 
                    font-size: 30px; 
                    color: {COLORS['fg']}; 
                    background-color: transparent; 
                    border: none; 
                    padding: 10px; 
                    margin: 5px;
                    text-align: center;
                }}
                QPushButton:hover {{
                    color: {COLORS['highlight']};
                }}
                """
            )
            btn.clicked.connect(click_handler)
            return btn

        decks_btn = create_menu_button("Decks", "resources/decks.svg", self.on_decks_clicked)
        layout.addWidget(decks_btn, alignment=Qt.AlignCenter)

        stats_btn = create_menu_button("Stats", "resources/stats.svg", self.on_stats_clicked)
        layout.addWidget(stats_btn, alignment=Qt.AlignCenter)

        settings_btn = create_menu_button("Settings", "resources/gear.svg", self.on_settings_clicked)
        layout.addWidget(settings_btn, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def on_decks_clicked(self):
        self.parent().setCurrentIndex(1)

    def on_stats_clicked(self):
        self.parent().setCurrentIndex(2)

    def on_settings_clicked(self):
        self.parent().setCurrentIndex(3)

