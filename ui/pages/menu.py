from PyQt5.QtCore import QRect, Qt, QTimer
from PyQt5.QtGui import QColor, QFont, QFontMetrics, QIcon, QPainter, QPixmap
from PyQt5.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from ..components import create_colored_icon
from ..theme import COLORS, FONT_FAMILY

with open("resources/logo.txt", "r") as f:
    LOGO_CONTENT = f.read()


class InteractiveLogo(QWidget):
    """Logo widget where individual characters change color on hover."""

    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.text = text
        self.font = QFont("monospace", 12)
        self.char_rects = []  # Store position and size of each character
        self.hovered_char = -1  # Index of currently hovered character
        self.highlighted_chars = set()  # Characters that should remain highlighted
        self.char_timers = {}  # Timer for each character to clear highlight
        self.setMouseTracking(True)
        self._calculate_char_positions()

    def _calculate_char_positions(self):
        """Calculate the position and size of each character."""
        self.char_rects = []
        metrics = QFontMetrics(self.font)

        lines = self.text.split("\n")
        y_offset = 0

        for line in lines:
            x_offset = 0
            line_height = metrics.height()

            for char in line:
                char_width = metrics.horizontalAdvance(char)
                char_rect = QRect(x_offset, y_offset, char_width, line_height)
                self.char_rects.append((char, char_rect))
                x_offset += char_width

            y_offset += line_height

        # Set widget size based on text bounds
        if lines:
            max_width = max(metrics.horizontalAdvance(line) for line in lines)
            total_height = len(lines) * metrics.height()
            self.setFixedSize(max_width, total_height)

    def mouseMoveEvent(self, event):
        """Track which character is being hovered."""
        old_hovered = self.hovered_char
        self.hovered_char = -1

        for i, (char, rect) in enumerate(self.char_rects):
            if rect.contains(event.pos()):
                self.hovered_char = i
                # Add this character to highlighted set and start/restart timer
                self.highlighted_chars.add(i)
                self._start_char_timer(i)
                break

        # Only repaint if hover state changed
        if old_hovered != self.hovered_char:
            self.update()

    def _start_char_timer(self, char_index):
        """Start or restart the 2-second timer for a character."""
        # Stop existing timer if any
        if char_index in self.char_timers:
            self.char_timers[char_index].stop()

        # Create new timer
        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(lambda: self._clear_char_highlight(char_index))
        timer.start(2000)  # 2 seconds
        self.char_timers[char_index] = timer

    def _clear_char_highlight(self, char_index):
        """Clear highlight for a specific character."""
        if char_index in self.highlighted_chars:
            self.highlighted_chars.remove(char_index)
            self.update()
        if char_index in self.char_timers:
            del self.char_timers[char_index]

    def leaveEvent(self, event):
        """Clear hover state when mouse leaves widget."""
        if self.hovered_char != -1:
            self.hovered_char = -1
            self.update()
            # Note: highlighted_chars remain and will be cleared by their timers

    def paintEvent(self, event):
        """Custom paint to draw each character with appropriate color."""
        painter = QPainter(self)
        painter.setFont(self.font)

        for i, (char, rect) in enumerate(self.char_rects):
            # Use orange color for hovered character or highlighted characters
            if i == self.hovered_char or i in self.highlighted_chars:
                painter.setPen(QColor("#ff6b35"))  # Orange
            else:
                painter.setPen(QColor(COLORS["fg"]))  # Normal fg color

            painter.drawText(rect, Qt.AlignLeft | Qt.AlignTop, char)


class MenuPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background-color: {COLORS['bg_soft']};")

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        # Interactive logo where individual characters turn orange on hover
        logo = InteractiveLogo(LOGO_CONTENT, self)
        layout.addWidget(logo)

        def create_menu_button(text, icon_path, click_handler):
            btn = QPushButton(f"  {text}", self)  # Add spaces for icon-text spacing
            btn.setIcon(create_colored_icon(icon_path, COLORS["highlight"], 24))
            btn.setStyleSheet(
                f"""
                QPushButton {{
                    font-family: {FONT_FAMILY}; 
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

        decks_btn = create_menu_button(
            "Decks", "resources/decks.svg", self.on_decks_clicked
        )
        layout.addWidget(decks_btn, alignment=Qt.AlignCenter)

        stats_btn = create_menu_button(
            "Stats", "resources/stats.svg", self.on_stats_clicked
        )
        layout.addWidget(stats_btn, alignment=Qt.AlignCenter)

        settings_btn = create_menu_button(
            "Settings", "resources/gear.svg", self.on_settings_clicked
        )
        layout.addWidget(settings_btn, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def on_decks_clicked(self):
        self.parent().setCurrentIndex(1)

    def on_stats_clicked(self):
        self.parent().setCurrentIndex(2)

    def on_settings_clicked(self):
        self.parent().setCurrentIndex(3)
