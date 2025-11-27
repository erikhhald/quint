#!/usr/bin/env python3
import sys

from PyQt5.QtGui import QFontDatabase
from PyQt5.QtWidgets import QApplication

from ui import theme
from ui.pages.main_window import MainApp


def load_fonts():
    """Load custom fonts for the application."""
    font_db = QFontDatabase()

    # Load JetBrains Mono font
    font_path = "resources/JetBrainsMono-VariableFont_wght.ttf"
    font_id = font_db.addApplicationFont(font_path)

    if font_id != -1:
        font_families = font_db.applicationFontFamilies(font_id)
        print(f"Loaded font: {font_families}")
        return font_families[0] if font_families else "JetBrains Mono"
    else:
        print("Failed to load JetBrains Mono font, falling back to monospace")
        return "monospace"


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Load custom fonts
    font_family = load_fonts()
    theme.FONT_FAMILY = font_family

    window = MainApp()
    window.show()
    sys.exit(app.exec_())

