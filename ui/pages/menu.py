from PyQt5.QtCore import QRect, Qt, QTimer
from PyQt5.QtGui import QColor, QFont, QFontMetrics, QIcon, QPainter, QPixmap
from PyQt5.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from ..components import create_colored_icon
from ..template import GenericPage
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
        self.lines = []  # Store lines for calculating grid positions
        self.hovered_char = -1  # Index of currently hovered character
        self.highlighted_chars = (
            {}
        )  # Characters that should remain highlighted with fade level
        self.char_timers = {}  # Timer for each character to clear highlight
        self.grace_timers = {}  # Grace period timers before fade starts
        self.setMouseTracking(True)
        self._calculate_char_positions()

    def _calculate_char_positions(self):
        """Calculate the position and size of each character."""
        self.char_rects = []
        self.lines = self.text.split("\n")
        metrics = QFontMetrics(self.font)

        y_offset = 0
        char_index = 0

        for line_idx, line in enumerate(self.lines):
            x_offset = 0
            line_height = metrics.height()

            for char_idx, char in enumerate(line):
                char_width = metrics.horizontalAdvance(char)
                char_rect = QRect(x_offset, y_offset, char_width, line_height)
                self.char_rects.append((char, char_rect, line_idx, char_idx))
                x_offset += char_width
                char_index += 1

            y_offset += line_height

        # Set widget size based on text bounds
        if self.lines:
            max_width = max(metrics.horizontalAdvance(line) for line in self.lines)
            total_height = len(self.lines) * metrics.height()
            self.setFixedSize(max_width, total_height)

    def mouseMoveEvent(self, event):
        """Track which character is being hovered."""
        old_hovered = self.hovered_char
        self.hovered_char = -1

        for i, (char, rect, line_idx, char_idx) in enumerate(self.char_rects):
            if rect.contains(event.pos()):
                self.hovered_char = i
                # Highlight 3x3 grid around this character
                self._highlight_surrounding_chars(line_idx, char_idx)
                break

        # Only repaint if hover state changed
        if old_hovered != self.hovered_char:
            self.update()

    def _highlight_surrounding_chars(self, center_line, center_char):
        """Highlight the 3x3 grid of characters around the center position."""
        for line_offset in [-1, 0, 1]:
            for char_offset in [-1, 0, 1]:
                target_line = center_line + line_offset
                target_char = center_char + char_offset

                # Find the character index for this position
                char_index = self._get_char_index(target_line, target_char)
                if char_index is not None:
                    self.highlighted_chars[char_index] = 1.0
                    self._start_grace_period(char_index)

    def _get_char_index(self, line_idx, char_idx):
        """Get the global character index for a given line and character position."""
        if 0 <= line_idx < len(self.lines) and 0 <= char_idx < len(
            self.lines[line_idx]
        ):
            char_index = 0
            for i in range(line_idx):
                char_index += len(self.lines[i])
            char_index += char_idx
            return char_index
        return None

    def _start_grace_period(self, char_index):
        """Start the 2-second grace period before fading begins."""
        # Stop existing timers if any
        if char_index in self.grace_timers:
            self.grace_timers[char_index].stop()
        if char_index in self.char_timers:
            self.char_timers[char_index].stop()

        # Create grace period timer (2 seconds)
        grace_timer = QTimer()
        grace_timer.setSingleShot(True)
        grace_timer.timeout.connect(lambda: self._start_fade_timer(char_index))
        grace_timer.start(2000)  # 2 seconds
        self.grace_timers[char_index] = grace_timer

    def _start_fade_timer(self, char_index):
        """Start the fade timer for a character after grace period."""
        # Remove grace timer
        if char_index in self.grace_timers:
            del self.grace_timers[char_index]

        # Create fade timer that fires every 0.25 seconds
        timer = QTimer()
        timer.timeout.connect(lambda: self._fade_char(char_index))
        timer.start(250)  # 0.25 seconds
        self.char_timers[char_index] = timer

    def _fade_char(self, char_index):
        if char_index in self.highlighted_chars:
            current_intensity = self.highlighted_chars[char_index]
            new_intensity = current_intensity - 0.25  # 25% reduction per step

            if new_intensity <= 0:
                # Fully faded, remove highlight
                del self.highlighted_chars[char_index]
                if char_index in self.char_timers:
                    self.char_timers[char_index].stop()
                    del self.char_timers[char_index]
                if char_index in self.grace_timers:
                    self.grace_timers[char_index].stop()
                    del self.grace_timers[char_index]
            else:
                # Update intensity
                self.highlighted_chars[char_index] = new_intensity

            self.update()

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

        for i, (char, rect, line_idx, char_idx) in enumerate(self.char_rects):
            # Determine color based on highlight state
            if i == self.hovered_char:
                # Currently hovered character - full orange
                painter.setPen(QColor("#ff6b35"))
            elif i in self.highlighted_chars:
                # Fading highlighted character - interpolate between orange and normal
                intensity = self.highlighted_chars[i]
                orange = QColor("#ff6b35")
                normal = QColor(COLORS["fg"])

                # Interpolate between colors based on intensity
                r = int(normal.red() + (orange.red() - normal.red()) * intensity)
                g = int(normal.green() + (orange.green() - normal.green()) * intensity)
                b = int(normal.blue() + (orange.blue() - normal.blue()) * intensity)

                painter.setPen(QColor(r, g, b))
            else:
                # Normal color
                painter.setPen(QColor(COLORS["fg"]))

            painter.drawText(rect, Qt.AlignLeft | Qt.AlignTop, char)


class MenuPage(GenericPage):
    def __init__(self):
        super().__init__()

        # Hide back button for main menu, keep close button
        self.back_btn.hide()

        # Add stretch to push content to center
        self.add_stretch()

        # Interactive logo where individual characters turn orange on hover
        logo = InteractiveLogo(LOGO_CONTENT, self)
        self.add_widget(logo, alignment=Qt.AlignCenter)

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
        self.add_widget(decks_btn, alignment=Qt.AlignCenter)

        stats_btn = create_menu_button(
            "Stats", "resources/stats.svg", self.on_stats_clicked
        )
        self.add_widget(stats_btn, alignment=Qt.AlignCenter)

        settings_btn = create_menu_button(
            "Settings", "resources/gear.svg", self.on_settings_clicked
        )
        self.add_widget(settings_btn, alignment=Qt.AlignCenter)

        # Add stretch at bottom to center content vertically
        self.add_stretch()

    def on_decks_clicked(self):
        self.parent().setCurrentIndex(1)

    def on_stats_clicked(self):
        self.parent().setCurrentIndex(2)

    def on_settings_clicked(self):
        self.parent().setCurrentIndex(3)
