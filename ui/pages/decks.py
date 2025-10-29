from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from database import services

from ..components import create_back_button, create_title_label
from ..theme import COLORS


class DecksPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background-color: {COLORS['bg_soft']};")

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        # Floating back button
        back_btn = create_back_button(parent=self)
        back_btn.clicked.connect(self.on_back_clicked)

        # Title with icon
        title = create_title_label("Decks", self, "resources/decks.svg")
        layout.addWidget(title)

        # Get deck data from database
        deck_data = services.get_all_deck_stats()

        # Store deck data for access in click handler
        self.deck_data = deck_data

        table = QTableWidget()
        table.setRowCount(len(deck_data))
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Deck", "New", "Due"])

        # Left-align the "Deck" header
        table.horizontalHeaderItem(0).setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # Remove row numbers and gridlines
        table.verticalHeader().setVisible(False)
        table.setShowGrid(False)

        # Disable scrollbars and auto-size to content
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        table.setSizePolicy(table.sizePolicy().Minimum, table.sizePolicy().Minimum)

        # Enable full row selection
        table.setSelectionBehavior(table.SelectRows)
        table.setMouseTracking(True)

        # Style the table
        table.setStyleSheet(
            f"""
            QTableWidget {{
                background-color: {COLORS['bg_soft']};
                color: {COLORS['fg']};
                font-family: monospace;
                font-size: 20px;
                border: none;
                outline: none;
            }}
            QHeaderView::section {{
                background-color: transparent;
                color: {COLORS['fg']};
                font-family: monospace;
                font-weight: bold;
                border: none;
            }}
            QTableWidget::item {{
                padding: 8px;
                border: none;
                background-color: transparent;
            }}
            QTableWidget::item:hover {{
                color: {COLORS['highlight']};
            }}
            QTableWidget::item:selected {{
                color: {COLORS['highlight']};
            }}
        """
        )

        # Populate table with data
        for row, data in enumerate(deck_data):
            deck_item = QTableWidgetItem(data["name"])
            deck_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            table.setItem(row, 0, deck_item)

            new_item = QTableWidgetItem(str(data["new"]))
            new_item.setTextAlignment(Qt.AlignCenter)
            table.setItem(row, 1, new_item)

            due_item = QTableWidgetItem(str(data["due"]))
            due_item.setTextAlignment(Qt.AlignCenter)
            table.setItem(row, 2, due_item)

        # Auto-resize columns to content
        table.resizeColumnsToContents()
        table.resizeRowsToContents()

        # Set column widths (make wider)
        table.setColumnWidth(0, max(table.columnWidth(0), 400))
        table.setColumnWidth(1, max(table.columnWidth(1), 80))
        table.setColumnWidth(2, max(table.columnWidth(2), 80))

        # Resize table to fit contents exactly
        table.setFixedSize(
            table.horizontalHeader().length() + 20,
            table.verticalHeader().length() + table.horizontalHeader().height() + 10,
        )

        # Connect table click to open chat
        table.cellClicked.connect(self.on_deck_clicked)

        # Center the table in the layout
        layout.addWidget(table, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def on_back_clicked(self):
        self.parent().setCurrentIndex(0)

    def on_deck_clicked(self, row, column):
        # Get the deck data from the clicked row
        deck_data = self.deck_data[row]
        deck_id = deck_data["id"]
        deck_name = deck_data["name"]

        # Navigate to chat page and pass deck info
        chat_page = self.parent().parent().chat_page
        chat_page.set_deck(deck_name, deck_id)
        self.parent().setCurrentIndex(4)
