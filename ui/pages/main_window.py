from PyQt5.QtWidgets import QVBoxLayout, QStackedWidget, QApplication
from PyQt5.QtCore import Qt
from ..template import GenericPage
from ..theme import COLORS
from .menu import MenuPage
from .decks import DecksPage
from .chat import ChatPage
from .stats import StatsPage
from .settings import SettingsPage

class MainApp(GenericPage):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowCloseButtonHint)
        self.setWindowTitle("Quint")
        
        # Hide the back button since this is the main window
        self.back_btn.hide()

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

        self.add_widget(self.stacked_widget)

        # Set window size to 1600x1200 or fullscreen if monitor is smaller
        self.setMinimumSize(1600, 1200)

        app = QApplication.instance()
        if app:
            screen = app.primaryScreen()
            if screen:
                screen_size = screen.availableGeometry()

                if screen_size.width() >= 1600 and screen_size.height() >= 1200:
                    self.setGeometry(
                        (screen_size.width() - 1600) // 2,
                        (screen_size.height() - 1200) // 2,
                        1600,
                        1200,
                    )
                else:
                    self.showMaximized()
            else:
                self.resize(1600, 1200)
        else:
            self.resize(1600, 1200)