#!/usr/bin/env python3
import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())