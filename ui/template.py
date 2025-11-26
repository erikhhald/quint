from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QWidget

from .components import create_back_button
from .theme import COLORS, FONT_FAMILY


class GenericPage(QWidget):
    """Generic page template with back button functionality."""

    def __init__(self, title=None, icon_path=None):
        super().__init__()
        self.setStyleSheet(f"background-color: {COLORS['bg_soft']};")

        # Main layout
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)

        # Add title if provided
        if title:
            from .components import create_title_label

            title_widget = create_title_label(title, self, icon_path)
            self.layout.addWidget(title_widget)

        self.setLayout(self.layout)

        # Create floating back button AFTER layout is set to ensure it's on top
        self.back_btn = create_back_button(parent=self)
        self.back_btn.clicked.connect(self.on_back_clicked)
        # Force the button to stay on top
        self.back_btn.raise_()

        # Create floating X button in top right corner
        self.close_btn = QPushButton("✕", self)
        self.close_btn.setFixedSize(40, 40)
        self.close_btn.setStyleSheet(
            f"""
            QPushButton {{
                font-family: {FONT_FAMILY};
                font-size: 20px;
                color: {COLORS['fg']};
                background-color: transparent;
                border: 2px solid {COLORS['fg_faded']};
                border-radius: 20px;
                position: absolute;
            }}
            QPushButton:hover {{
                color: {COLORS['highlight']};
                border-color: {COLORS['highlight']};
                background-color: {COLORS['bg_hard']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['fg_faded']};
            }}
        """
        )
        self.close_btn.clicked.connect(self.on_close_clicked)
        self.close_btn.raise_()

    def resizeEvent(self, event):
        """Position the close button in the top right corner when window resizes."""
        super().resizeEvent(event)
        if hasattr(self, "close_btn"):
            self.close_btn.move(self.width() - 50, 10)

    def on_back_clicked(self):
        """Handle back button click - navigate to main menu (index 0)."""
        self.parent().setCurrentIndex(0)

    def on_close_clicked(self):
        """Handle close button click - close the window."""
        self.window().close()

    def add_widget(self, widget, alignment=None):
        """Add a widget to the main layout."""
        if alignment:
            self.layout.addWidget(widget, alignment=alignment)
        else:
            self.layout.addWidget(widget)

    def add_layout(self, layout):
        """Add a layout to the main layout."""
        self.layout.addLayout(layout)

    def add_stretch(self):
        """Add stretch to the main layout."""
        self.layout.addStretch()
