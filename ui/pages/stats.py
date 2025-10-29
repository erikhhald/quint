from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from ..components import create_back_button, create_title_label
from ..theme import COLORS

class StatsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background-color: {COLORS['bg_soft']};")

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        # Floating back button
        back_btn = create_back_button(parent=self)
        back_btn.clicked.connect(self.on_back_clicked)

        title = create_title_label("Stats", self, "resources/stats.svg")
        layout.addWidget(title)

        self.setLayout(layout)

    def on_back_clicked(self):
        self.parent().setCurrentIndex(0)