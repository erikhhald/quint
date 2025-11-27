from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QWidget

from .components import BackButton, TitleLabel
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
            title_widget = TitleLabel(title, self, icon_path)
            self.layout.addWidget(title_widget)

        self.setLayout(self.layout)

        # Create floating back button AFTER layout is set to ensure it's on top
        self.back_btn = BackButton(parent=self, floating=True)
        self.back_btn.clicked.connect(self.on_back_clicked)
        # Force the button to stay on top
        self.back_btn.raise_()


    def resizeEvent(self, event):
        """Handle resize event."""
        super().resizeEvent(event)

    def on_back_clicked(self):
        """Handle back button click - navigate to main menu (index 0)."""
        self.parent().setCurrentIndex(0)


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
