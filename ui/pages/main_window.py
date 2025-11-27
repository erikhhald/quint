from PyQt5.QtWidgets import QVBoxLayout, QStackedWidget, QApplication, QWidget
from PyQt5.QtCore import Qt
from ..theme import COLORS
from .menu import MenuPage
from .decks import DecksPage
from .chat import ChatPage
from .stats import StatsPage
from .settings import SettingsPage
from settings.settings import settings

class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        self.setWindowTitle("Quint")
        self.setStyleSheet(f"background-color: {COLORS['bg_soft']};")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.stacked_widget = QStackedWidget()

        self.menu_page = MenuPage()
        self.decks_page = DecksPage()
        self.stats_page = StatsPage()
        self.settings_page = SettingsPage()
        self.chat_page = ChatPage()

        self.stacked_widget.addWidget(self.menu_page)
        self.stacked_widget.addWidget(self.decks_page)
        self.stacked_widget.addWidget(self.stats_page)
        self.stacked_widget.addWidget(self.settings_page)
        self.stacked_widget.addWidget(self.chat_page)

        layout.addWidget(self.stacked_widget)
        self.setLayout(layout)

        # Set window size and position from settings
        self.setMinimumSize(800, 600)
        self.resize(settings.window_width, settings.window_height)

        # Position window from saved settings or center it
        if settings.window_x >= 0 and settings.window_y >= 0:
            self.move(settings.window_x, settings.window_y)
        else:
            app = QApplication.instance()
            if app:
                screen = app.primaryScreen()
                if screen:
                    screen_size = screen.availableGeometry()
                    if screen_size.width() >= settings.window_width and screen_size.height() >= settings.window_height:
                        self.move(
                            (screen_size.width() - settings.window_width) // 2,
                            (screen_size.height() - settings.window_height) // 2,
                        )
                    else:
                        self.showMaximized()

    def closeEvent(self, event):
        """Save window size and position before closing."""
        # Save current window geometry to settings
        geometry = self.geometry()
        settings.window_width = geometry.width()
        settings.window_height = geometry.height()
        settings.window_x = geometry.x()
        settings.window_y = geometry.y()
        
        # Accept the close event
        event.accept()