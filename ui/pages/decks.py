from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QIcon
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from database import services

from ..components import create_back_button, create_colored_icon, create_title_label
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
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Deck", "New", "Due", ""])

        # Left-align the "Deck" header
        table.horizontalHeaderItem(0).setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # Remove row numbers and gridlines
        table.verticalHeader().setVisible(False)
        table.setShowGrid(False)

        # Disable scrollbars and auto-size to content
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        table.setSizePolicy(table.sizePolicy().Minimum, table.sizePolicy().Minimum)

        # Disable selection
        table.setSelectionMode(QTableWidget.NoSelection)
        table.setMouseTracking(True)

        # Style the table with alternating row colors
        table.setStyleSheet(
            f"""
            QTableWidget {{
                background-color: {COLORS['bg_soft']};
                color: {COLORS['fg']};
                font-family: {FONT_FAMILY};
                font-size: 32px;
                border: none;
                outline: none;
                gridline-color: {COLORS['fg_dim']};
            }}
            QHeaderView::section {{
                background-color: {COLORS['bg_soft']};
                color: #ff6b35;
                font-family: {FONT_FAMILY};
                font-weight: bold;
                font-size: 32px;
                border: none;
                border-bottom: 2px solid {COLORS['bg_hard']};
                padding: 12px 8px;
                text-align: left;
            }}
            QTableWidget::item {{
                padding: 10px 10px;
                border: none;
            }}
            QTableWidget::item:selected {{
                background-color: transparent;
                color: inherit;
            }}
        """
        )

        for row, data in enumerate(deck_data):
            deck_item = QTableWidgetItem(data["name"])
            deck_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)

            table.setItem(row, 0, deck_item)

            new_item = QTableWidgetItem(str(data["new"]))
            new_item.setTextAlignment(Qt.AlignCenter)
            new_item.setFlags(
                new_item.flags() & ~Qt.ItemIsSelectable
            )  # Disable selection/hover
            # Color new count blue if there are new cards
            if data["new"] > 0:
                new_item.setForeground(QColor(COLORS["new_blue"]))
            else:
                new_item.setForeground(QColor(COLORS["fg_faded"]))

            table.setItem(row, 1, new_item)

            due_item = QTableWidgetItem(str(data["due"]))
            due_item.setTextAlignment(Qt.AlignCenter)
            due_item.setFlags(
                due_item.flags() & ~Qt.ItemIsSelectable
            )  # Disable selection/hover
            # Color due count yellow if there are due cards
            if data["due"] > 0:
                due_item.setForeground(QColor(COLORS["due_yellow"]))
            else:
                due_item.setForeground(QColor(COLORS["fg_faded"]))

            table.setItem(row, 2, due_item)

            # Add gear icon in the rightmost column
            gear_item = QTableWidgetItem("")
            gear_item.setTextAlignment(Qt.AlignCenter)
            # Create gear icon for this cell
            gear_icon = create_colored_icon("resources/gear.svg", COLORS["fg"], 32)
            gear_item.setIcon(gear_icon)
            table.setItem(row, 3, gear_item)

        # Auto-resize columns to content
        table.resizeColumnsToContents()
        table.resizeRowsToContents()

        # Set column widths (make wider)
        table.setColumnWidth(0, max(table.columnWidth(0), 600))
        table.setColumnWidth(1, max(table.columnWidth(1), 120))
        table.setColumnWidth(2, max(table.columnWidth(2), 120))
        table.setColumnWidth(3, 100)  # Fixed width for gear icon column

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

        # Add table to container
        table_layout.addWidget(table)

        # Add button below table
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 10, 0, 0)
        # Button will be flush with left side of table

        # New deck button (smaller, below table)
        new_deck_btn = QPushButton("+", self)
        new_deck_btn.setFixedSize(80, 50)  # 1.5 x height ratio
        new_deck_btn.setStyleSheet(
            f"""
            QPushButton {{
                font-family: {FONT_FAMILY};
                font-size: 24px;
                color: white;
                background-color: #ff6b35;
                border: none;
                border-radius: 8px;
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
        button_layout.addWidget(new_deck_btn)
        button_layout.addStretch()  # Push everything else to the right

        table_layout.addLayout(button_layout)

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
        """Handle new deck button click - prompt for deck name."""
        deck_name, ok = QInputDialog.getText(
            self, "New Deck", "Enter deck name:", text="My New Deck"
        )

        if ok and deck_name.strip():
            try:
                # Create the new deck in database
                deck_id = services.create_deck(deck_name.strip())
                if deck_id:
                    QMessageBox.information(
                        self, "Success", f'Deck "{deck_name}" created successfully!'
                    )
                    # Refresh the page to show the new deck
                    self._refresh_deck_list()
                else:
                    QMessageBox.warning(
                        self, "Error", "Failed to create deck. Please try again."
                    )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error creating deck: {str(e)}")
        elif ok:  # User clicked OK but entered empty name
            QMessageBox.warning(self, "Invalid Name", "Deck name cannot be empty.")

    def _refresh_deck_list(self):
        """Refresh the deck table with latest data."""
        # Get updated deck data
        deck_data = services.get_all_deck_stats()
        self.deck_data = deck_data

        # Find the table widget and update it
        for widget in self.findChildren(QTableWidget):
            # Clear and repopulate table
            widget.setRowCount(len(deck_data))
            widget.setColumnCount(4)

            special_decks = ["Art History", "Biology - Cell Structure"]

            for row, data in enumerate(deck_data):
                deck_item = QTableWidgetItem(data["name"])
                deck_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)

                if data["name"] in special_decks:
                    deck_item.setForeground(QColor("#ff6b35"))

                widget.setItem(row, 0, deck_item)

                new_item = QTableWidgetItem(str(data["new"]))
                new_item.setTextAlignment(Qt.AlignCenter)
                new_item.setFlags(
                    new_item.flags() & ~Qt.ItemIsSelectable
                )  # Disable selection/hover
                if data["new"] > 0:
                    new_item.setForeground(QColor(COLORS["new_blue"]))
                else:
                    new_item.setForeground(QColor(COLORS["fg_faded"]))
                widget.setItem(row, 1, new_item)

                due_item = QTableWidgetItem(str(data["due"]))
                due_item.setTextAlignment(Qt.AlignCenter)
                due_item.setFlags(
                    due_item.flags() & ~Qt.ItemIsSelectable
                )  # Disable selection/hover
                if data["due"] > 0:
                    due_item.setForeground(QColor(COLORS["due_yellow"]))
                else:
                    due_item.setForeground(QColor(COLORS["fg_faded"]))
                widget.setItem(row, 2, due_item)

                # Add gear icon in the rightmost column
                gear_item = QTableWidgetItem("")
                gear_item.setTextAlignment(Qt.AlignCenter)
                gear_icon = create_colored_icon(
                    "resources/gear.svg", COLORS["fg_dim"], 20
                )
                gear_item.setIcon(gear_icon)
                widget.setItem(row, 3, gear_item)

            break

    def on_deck_clicked(self, row, column):
        # Get the deck data from the clicked row
        deck_data = self.deck_data[row]
        deck_id = deck_data["id"]
        deck_name = deck_data["name"]

        # Navigate to chat page and pass deck info
        chat_page = self.parent().parent().chat_page
        chat_page.set_deck(deck_name, deck_id)
        self.parent().setCurrentIndex(4)
