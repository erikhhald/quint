from PyQt5.QtWidgets import QWidget, QVBoxLayout, QStackedWidget, QApplication
from .theme import COLORS
from .pages.menu import MenuPage
from .pages.decks import DecksPage
from .pages.chat import ChatPage
from .pages.stats import StatsPage
from .pages.settings import SettingsPage

class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quint")
        self.setStyleSheet(f"background-color: {COLORS['bg_soft']};")

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

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.stacked_widget)
        self.setLayout(main_layout)

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