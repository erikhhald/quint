from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QHBoxLayout,
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
from ..theme import COLORS, FONT_FAMILY


class DecksPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background-color: {COLORS['bg_soft']};")

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

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

        # Style the table with alternating row colors
        table.setStyleSheet(
            f"""
            QTableWidget {{
                background-color: {COLORS['bg_soft']};
                color: {COLORS['fg']};
                font-family: {FONT_FAMILY};
                font-size: 18px;
                border: none;
                outline: none;
                gridline-color: {COLORS['fg_dim']};
            }}
            QHeaderView::section {{
                background-color: {COLORS['bg_hard']};
                color: {COLORS['fg']};
                font-family: {FONT_FAMILY};
                font-weight: bold;
                font-size: 16px;
                border: none;
                padding: 12px 8px;
                text-align: left;
            }}
            QTableWidget::item {{
                padding: 12px 8px;
                border: none;
                border-bottom: 1px solid {COLORS['bg_hard']};
            }}
            QTableWidget::item:hover {{
                background-color: {COLORS['bg_hard']};
            }}
            QTableWidget::item:selected {{
                background-color: {COLORS['bg_hard']};
                color: {COLORS['highlight']};
            }}
        """
        )

        for row, data in enumerate(deck_data):
            deck_item = QTableWidgetItem(data["name"])
            deck_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)

            table.setItem(row, 0, deck_item)

            new_item = QTableWidgetItem(str(data["new"]))
            new_item.setTextAlignment(Qt.AlignCenter)
            # Color new count orange if there are new cards
            if data["new"] > 0:
                new_item.setStyleSheet(f"color: #ff6b35; font-weight: bold;")
            table.setItem(row, 1, new_item)

            due_item = QTableWidgetItem(str(data["due"]))
            due_item.setTextAlignment(Qt.AlignCenter)
            # Color due count orange if there are due cards
            if data["due"] > 0:
                due_item.setStyleSheet(f"color: #ff6b35; font-weight: bold;")
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

        # Create container for table and header alignment
        table_container = QWidget()
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(0, 0, 0, 0)

        # Header aligned with table
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 10)

        # Deck label (left aligned with table)
        deck_label = QLabel("Decks")
        deck_label.setStyleSheet(
            f"font-family: {FONT_FAMILY}; font-size: 32px; color: {COLORS['fg']}; font-weight: bold;"
        )
        header_layout.addWidget(deck_label)

        # Spacer
        header_layout.addStretch()

        # New deck button (right aligned with table)
        new_deck_btn = QPushButton("+", self)
        new_deck_btn.setStyleSheet(
            f"""
            QPushButton {{
                font-family: {FONT_FAMILY};
                font-size: 32px;
                color: white;
                background-color: #ff6b35;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background-color: #e55a2b;
            }}
            QPushButton:pressed {{
                background-color: #cc4d24;
            }}
            """
        )
        new_deck_btn.clicked.connect(self.on_new_deck_clicked)
        header_layout.addWidget(new_deck_btn)

        # Add header and table to container
        table_layout.addLayout(header_layout)
        table_layout.addWidget(table)

        # Center the entire container
        layout.addWidget(table_container, alignment=Qt.AlignCenter)

        self.setLayout(layout)

        # Create floating back button AFTER layout is set to ensure it's on top
        back_btn = create_back_button(parent=self)
        back_btn.clicked.connect(self.on_back_clicked)
        # Force the button to stay on top
        back_btn.raise_()

    def on_back_clicked(self):
        self.parent().setCurrentIndex(0)

    def on_new_deck_clicked(self):
        print("New deck button clicked")  # Placeholder

    def on_deck_clicked(self, row, column):
        # Get the deck data from the clicked row
        deck_data = self.deck_data[row]
        deck_id = deck_data["id"]
        deck_name = deck_data["name"]

        # Navigate to chat page and pass deck info
        chat_page = self.parent().parent().chat_page
        chat_page.set_deck(deck_name, deck_id)
        self.parent().setCurrentIndex(4)
