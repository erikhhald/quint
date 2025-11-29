import asyncio

from PyQt5.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
    Qt,
    QThread,
    QTimer,
    pyqtSignal,
)
from PyQt5.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from database import services
from flows.chat import process_study_card

from ..components import FileSelector, create_colored_icon
from ..template import GenericPage
from ..theme import COLORS, FONT_FAMILY


class AsyncWorker(QThread):
    """Worker thread for async operations."""

    message_ready = pyqtSignal(str, bool)  # message, is_user
    clear_chat = pyqtSignal()
    scroll_to_bottom = pyqtSignal()
    error_occurred = pyqtSignal(str)
    loading_state_changed = pyqtSignal(bool)  # True for loading, False for idle

    def __init__(self, deck_id):
        super().__init__()
        self.deck_id = deck_id
        self._user_input_future = None
        self._event_loop = None
        self.is_loading = False

    def run(self):
        """Run the async operation in a separate thread."""
        try:
            # Create event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self._event_loop = loop

            # Start in loading state
            self.set_loading(True)

            # Run the async function, passing self as the worker
            loop.run_until_complete(process_study_card(self.deck_id, self))

        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            # End in non-loading state
            self.set_loading(False)
            loop.close()

    async def wait_for_user_input(self):
        """Wait for user input from the chat interface."""
        print("wait_for_user_input called")
        # Set loading to false while waiting for user input
        self.set_loading(False)

        # Create a future to wait for user input
        print("Creating future for user input")
        self._user_input_future = self._event_loop.create_future()
        print(f"Future created: {self._user_input_future}")

        print("Waiting for future to complete...")
        result = await self._user_input_future
        print(f"Future completed with result: {result}")

        # Set loading to true after receiving user input
        self.set_loading(True)

        return result

    def provide_user_input(self, user_input: str):
        """Provide user input to resolve the waiting future."""
        print(f"provide_user_input called with: {user_input}")
        print(f"_user_input_future exists: {self._user_input_future is not None}")
        if self._user_input_future:
            print(f"_user_input_future done: {self._user_input_future.done()}")
        
        if self._user_input_future and not self._user_input_future.done() and self._event_loop:
            print("Setting result on future via call_soon_threadsafe")
            # Use call_soon_threadsafe to set the result from the main thread
            self._event_loop.call_soon_threadsafe(self._user_input_future.set_result, user_input)
        else:
            print("Future is None, already done, or no event loop")

    def set_loading(self, loading: bool):
        """Set loading state and emit signal."""
        self.is_loading = loading
        self.loading_state_changed.emit(loading)


class LoadingDots(QWidget):
    """Simple loading dots widget."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_dot = 0
        self.timer = QTimer()
        self.dots = []
        self.setup_ui()
        
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(8)
        
        # Create three dots
        for i in range(3):
            dot = QLabel("●")
            dot.setStyleSheet(f"""
                QLabel {{
                    color: {COLORS['fg_dim']};
                    font-size: 20px;
                }}
            """)
            dot.setAlignment(Qt.AlignCenter)
            layout.addWidget(dot)
            self.dots.append(dot)
        
        layout.addStretch()
        
    def start_animation(self):
        """Start simple dot cycling animation."""
        self.timer.timeout.connect(self._animate_dot)
        self.timer.start(500)  # Change dot every 500ms
        
    def stop_animation(self):
        """Stop the animation."""
        self.timer.stop()
        # Reset all dots to dim color
        for dot in self.dots:
            dot.setStyleSheet(f"""
                QLabel {{
                    color: {COLORS['fg_dim']};
                    font-size: 20px;
                }}
            """)
        
    def _animate_dot(self):
        """Simple animation - cycle through dots."""
        # Reset all dots to dim
        for dot in self.dots:
            dot.setStyleSheet(f"""
                QLabel {{
                    color: {COLORS['fg_dim']};
                    font-size: 20px;
                }}
            """)
        
        # Highlight current dot
        if self.current_dot < len(self.dots):
            self.dots[self.current_dot].setStyleSheet(f"""
                QLabel {{
                    color: {COLORS['highlight']};
                    font-size: 20px;
                    font-weight: bold;
                }}
            """)
        
        # Move to next dot
        self.current_dot = (self.current_dot + 1) % len(self.dots)


class ChatBubble(QWidget):
    """A chat bubble widget that can be positioned on left or right side."""

    def __init__(self, message, is_user=False, parent=None):
        super().__init__(parent)
        self.message = message
        self.is_user = is_user
        self.setup_ui()

    def setup_ui(self):
        # Main layout for the bubble container
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 5, 20, 5)

        # Create the message bubble
        bubble = QFrame()
        bubble.setWordWrap = True

        # Set bubble alignment and width based on sender
        if self.is_user:
            # User message: align to right, orange theme
            main_layout.addStretch(1)  # 25% left space
            bubble.setStyleSheet(
                f"""
                QFrame {{
                    background-color: {COLORS['highlight']};
                    border: none;
                    border-radius: 15px;
                    padding: 15px 20px;
                    margin: 5px;
                }}
                """
            )
            text_color = COLORS["bg_hard"]
        else:
            # Assistant message: align to left, dark theme
            bubble.setStyleSheet(
                f"""
                QFrame {{
                    background-color: {COLORS['bg_hard']};
                    border: 1px solid {COLORS['fg_faded']};
                    border-radius: 15px;
                    padding: 15px 20px;
                    margin: 5px;
                }}
                """
            )
            text_color = COLORS["fg"]

        # Create message text
        bubble_layout = QVBoxLayout(bubble)
        bubble_layout.setContentsMargins(0, 0, 0, 0)

        message_label = QLabel(self.message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet(
            f"""
            QLabel {{
                font-family: {FONT_FAMILY};
                font-size: 32px;
                color: {text_color};
                background: transparent;
                border: none;
            }}
            """
        )
        bubble_layout.addWidget(message_label)

        # Add bubble with stretch factor 3 (75% width)
        main_layout.addWidget(bubble, 3)

        # Add stretch to opposite side
        if not self.is_user:
            main_layout.addStretch(1)  # 25% right space


class ChatPage(GenericPage):
    def __init__(self):
        super().__init__()

        # Override the back button with navigation back button and custom behavior
        self.back_btn.clicked.disconnect()  # Remove default behavior
        self.back_btn.clicked.connect(self.on_back_clicked)

        # Add card button positioned to the right of back button
        self.add_card_btn = QPushButton("+ Add Card", self)
        self.add_card_btn.setFixedSize(240, 40)  # 2x as long as back button
        self.add_card_btn.setStyleSheet(
            f"""
            QPushButton {{
                font-family: {FONT_FAMILY};
                font-size: 32px;
                font-weight: bold;
                color: {COLORS['highlight']};
                background-color: transparent;
                border: 2px solid {COLORS['highlight']};
                border-radius: 20px;
                padding: 8px 16px;
                min-width: 60px;
                min-height: 40px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['highlight']};
                color: {COLORS['bg_soft']};
                border: 2px solid {COLORS['highlight']};
            }}
            QPushButton:pressed {{
                background-color: #e55a2b;
                color: {COLORS['bg_soft']};
                border: 2px solid #e55a2b;
            }}
        """
        )
        self.add_card_btn.clicked.connect(self.on_add_card_clicked)
        # Position it to the right of the back button with proper spacing
        self.add_card_btn.move(
            140, 10
        )  # Further right, same vertical alignment as back button
        self.add_card_btn.raise_()  # Bring to front

        # Manage button positioned to the right of add card button
        self.manage_btn = QPushButton("Manage", self)
        self.manage_btn.setFixedSize(240, 40)  # Same size as add card button
        self.manage_btn.setStyleSheet(
            f"""
            QPushButton {{
                font-family: {FONT_FAMILY};
                font-size: 32px;
                font-weight: bold;
                color: {COLORS['highlight']};
                background-color: transparent;
                border: 2px solid {COLORS['highlight']};
                border-radius: 20px;
                padding: 8px 16px;
                min-width: 60px;
                min-height: 40px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['highlight']};
                color: {COLORS['bg_soft']};
                border: 2px solid {COLORS['highlight']};
            }}
            QPushButton:pressed {{
                background-color: #e55a2b;
                color: {COLORS['bg_soft']};
                border: 2px solid #e55a2b;
            }}
        """
        )
        self.manage_btn.clicked.connect(self.on_manage_clicked)
        # Position it to the right of add card button
        self.manage_btn.move(
            390, 10
        )  # 140 (add card position) + 240 (add card width) + 10 (spacing)
        self.manage_btn.raise_()  # Bring to front

        # Create scrollable chat area that takes full height
        self.chat_scroll = QScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.chat_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.chat_scroll.setStyleSheet(
            f"""
            QScrollArea {{
                border: none;
                background-color: transparent;
                margin-top: 110px;
                margin-left: 20px;
                margin-right: 20px;
                margin-bottom: 20px;
            }}
            """
        )

        # Chat content widget
        self.chat_content = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_content)
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.chat_layout.setSpacing(5)
        self.chat_layout.setContentsMargins(0, 20, 0, 20)

        # Add start button instead of welcome message
        self.start_button = QPushButton("Let's Start Studying!")
        self.start_button.setStyleSheet(
            f"""
            QPushButton {{
                font-family: {FONT_FAMILY};
                font-size: 32px;
                font-weight: bold;
                color: {COLORS['highlight']};
                background-color: transparent;
                border: 2px solid {COLORS['highlight']};
                border-radius: 15px;
                padding: 20px 40px;
                margin: 50px;
                min-height: 80px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['highlight']};
                color: {COLORS['bg_soft']};
                border: 2px solid {COLORS['highlight']};
            }}
            QPushButton:pressed {{
                background-color: #e55a2b;
                color: {COLORS['bg_soft']};
                border: 2px solid #e55a2b;
            }}
            """
        )
        self.start_button.clicked.connect(self.on_start_study)

        # Create a centered layout for the button
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.addStretch()
        button_layout.addWidget(self.start_button)
        button_layout.addStretch()

        self.chat_layout.addStretch()
        self.chat_layout.addWidget(button_container)
        self.chat_layout.addStretch()

        self.chat_scroll.setWidget(self.chat_content)
        self.add_widget(self.chat_scroll)

        # Ensure buttons stay on top
        self.back_btn.raise_()
        self.add_card_btn.raise_()
        self.manage_btn.raise_()

        # Chat input area
        input_layout = QHBoxLayout()

        self.chat_input = QLineEdit()
        self.chat_input.setText("> ")
        self.chat_input.setStyleSheet(
            f"""
            QLineEdit {{
                font-family: {FONT_FAMILY};
                font-size: 32px;
                color: {COLORS['fg']};
                background-color: {COLORS['bg_hard']};
                border: 1px solid {COLORS['fg_dim']};
                padding: 20px 30px;
                border-radius: 12px;
                selection-background-color: {COLORS['highlight']};
                selection-color: {COLORS['bg_hard']};
            }}
            QLineEdit:focus {{
                border: 1px solid {COLORS['highlight']};
            }}
            """
        )
        # Set custom cursor style to a solid box
        self.chat_input.setCursorPosition(2)  # Position after "> "
        self.chat_input.setStyleSheet(
            self.chat_input.styleSheet()
            + f"""
            QLineEdit {{
                selection-background-color: {COLORS['highlight']};
                selection-color: {COLORS['bg_hard']};
            }}
            """
        )
        self.chat_input.returnPressed.connect(self.send_message)
        # Set cursor position after the '> '
        self.chat_input.setCursorPosition(2)

        send_btn = QPushButton("Send")
        send_btn.setStyleSheet(
            f"""
            QPushButton {{
                font-family: {FONT_FAMILY};
                font-size: 32px;
                color: {COLORS['bg_hard']};
                background-color: {COLORS['highlight']};
                border: none;
                padding: 20px 40px;
                border-radius: 12px;
                margin-left: 10px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['fg']};
            }}
            """
        )
        send_btn.clicked.connect(self.send_message)

        input_layout.addWidget(self.chat_input)
        input_layout.addWidget(send_btn)

        # Create container for loading dots and input
        input_container = QVBoxLayout()
        input_container.setSpacing(5)
        input_container.setContentsMargins(0, 0, 0, 0)
        
        # Add a placeholder for loading dots (will be managed dynamically)
        self.loading_container = QWidget()
        self.loading_container_layout = QHBoxLayout(self.loading_container)
        self.loading_container_layout.setContentsMargins(0, 0, 0, 0)
        self.loading_container_layout.addStretch()  # This will be where loading dots go
        self.loading_container.setFixedHeight(0)  # Initially hidden
        
        input_container.addWidget(self.loading_container)
        input_container.addLayout(input_layout)

        self.add_layout(input_container)

    def set_deck(self, deck_name, deck_id=None):
        self.deck_name = deck_name
        self.deck_id = deck_id

    def on_back_clicked(self):
        self.parent().setCurrentIndex(1)

    def on_start_study(self):
        """Handle start study button click - start async card processing."""
        if not hasattr(self, "deck_id") or not self.deck_id:
            QMessageBox.warning(self, "No Deck Selected", "Please select a deck first.")
            return

        # Create and start async worker
        self.worker = AsyncWorker(self.deck_id)
        self.worker.message_ready.connect(self.add_message)
        self.worker.clear_chat.connect(self.clear_chat_area)
        self.worker.scroll_to_bottom.connect(self.scroll_to_bottom)
        self.worker.error_occurred.connect(self.handle_error)
        self.worker.loading_state_changed.connect(self.handle_loading_state)
        self.worker.start()

        # Initialize loading dots
        self.loading_dots = None

    def add_message(self, message: str, is_user: bool = False):
        """Add a message bubble to the chat."""
        bubble = ChatBubble(message, is_user=is_user)
        self.chat_layout.addWidget(bubble)

    def clear_chat_area(self):
        """Clear all messages from the chat area."""
        for i in reversed(range(self.chat_layout.count())):
            child = self.chat_layout.itemAt(i).widget()
            if child:
                child.setParent(None)

    def scroll_to_bottom(self):
        """Scroll chat to bottom."""
        self.chat_scroll.verticalScrollBar().setValue(
            self.chat_scroll.verticalScrollBar().maximum()
        )

    def handle_error(self, error_message: str):
        """Handle async operation errors."""
        QMessageBox.critical(
            self, "Error", f"Failed to load study card: {error_message}"
        )

    def handle_loading_state(self, is_loading: bool):
        """Handle loading state changes."""
        if is_loading:
            # Show loading dots
            if not self.loading_dots:
                self.loading_dots = LoadingDots()
                # Clear the stretch and add loading dots to the left
                for i in reversed(range(self.loading_container_layout.count())):
                    child = self.loading_container_layout.itemAt(i)
                    if child:
                        self.loading_container_layout.removeItem(child)
                
                self.loading_container_layout.addWidget(self.loading_dots)
                self.loading_container_layout.addStretch()  # Keep right side stretched
                self.loading_container.setFixedHeight(50)  # Make container visible
                self.loading_dots.start_animation()

            # Disable chat input
            self.chat_input.setEnabled(False)

        else:
            # Hide loading dots
            if self.loading_dots:
                self.loading_dots.stop_animation()
                self.loading_dots.setParent(None)
                self.loading_dots = None
                
                # Clear layout and add stretch back
                for i in reversed(range(self.loading_container_layout.count())):
                    child = self.loading_container_layout.itemAt(i)
                    if child:
                        self.loading_container_layout.removeItem(child)
                
                self.loading_container_layout.addStretch()
                self.loading_container.setFixedHeight(0)  # Hide container

            # Enable chat input
            self.chat_input.setEnabled(True)
            self.chat_input.setFocus()

        self.scroll_to_bottom()

    def on_manage_clicked(self):
        """Handle manage button click - show manage cards dialog."""
        if not hasattr(self, "deck_id") or not self.deck_id:
            QMessageBox.warning(self, "No Deck Selected", "Please select a deck first.")
            return

        dialog = ManageCardsDialog(self.deck_id, self)
        dialog.exec_()

    def on_add_card_clicked(self):
        """Handle add card button click - show add card dialog."""
        if not hasattr(self, "deck_id") or not self.deck_id:
            QMessageBox.warning(self, "No Deck Selected", "Please select a deck first.")
            return

        dialog = AddCardDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            file_path = dialog.get_file_path()
            copy_file = dialog.get_copy_option()

            if not file_path:
                QMessageBox.warning(self, "No File Selected", "Please select a file.")
                return

            try:
                # Create the card using the database service
                card = services.create_card(file_path, self.deck_id, copy_file)
                if card:
                    QMessageBox.information(
                        self,
                        "Success",
                        f'Card created successfully from "{file_path}"!',
                    )
                else:
                    QMessageBox.warning(
                        self, "Error", "Failed to create card. Please try again."
                    )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error creating card: {str(e)}")

    def send_message(self):
        # Don't send messages when loading
        if hasattr(self, "worker") and self.worker and self.worker.is_loading:
            return

        full_text = self.chat_input.text()
        # Extract message after the '> ' prefix
        message = (
            full_text[2:].strip() if full_text.startswith("> ") else full_text.strip()
        )
        if message:
            # Add user message bubble
            user_bubble = ChatBubble(message, is_user=True)
            self.chat_layout.addWidget(user_bubble)

            # If we have an active worker waiting for input, provide it
            if hasattr(self, "worker") and self.worker:
                self.worker.provide_user_input(message)
            else:
                # Fallback for when no worker is active
                response = f"You said: {message}"  # Placeholder response
                assistant_bubble = ChatBubble(response, is_user=False)
                self.chat_layout.addWidget(assistant_bubble)

            # Scroll to bottom
            self.chat_scroll.verticalScrollBar().setValue(
                self.chat_scroll.verticalScrollBar().maximum()
            )

            # Clear input
            self.chat_input.setText("> ")
            self.chat_input.setCursorPosition(2)


class AddCardDialog(QDialog):
    """Dialog for adding a new card to a deck."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Card")
        self.setModal(True)
        self.setMinimumSize(800, 400)
        self.resize(800, 400)

        # Set dialog styling
        self.setStyleSheet(f"background-color: {COLORS['bg_soft']};")

        layout = QVBoxLayout()

        # Title label
        title_label = QLabel("Add Card to Deck")
        title_label.setStyleSheet(
            f"""
            QLabel {{
                font-family: {FONT_FAMILY};
                font-size: 36px;
                font-weight: bold;
                color: {COLORS['fg']};
                margin-bottom: 20px;
            }}
            """
        )
        layout.addWidget(title_label)

        # File selector
        file_label = QLabel("Select File:")
        file_label.setStyleSheet(
            f"""
            QLabel {{
                font-family: {FONT_FAMILY};
                font-size: 36px;
                color: {COLORS['fg']};
                margin-bottom: 5px;
            }}
            """
        )
        layout.addWidget(file_label)

        self.file_selector = FileSelector("file", self)
        layout.addWidget(self.file_selector)

        # Copy checkbox
        self.copy_checkbox = QCheckBox("Copy file to managed store")
        self.copy_checkbox.setChecked(True)  # Default to copying
        self.copy_checkbox.setStyleSheet(
            f"""
            QCheckBox {{
                font-family: {FONT_FAMILY};
                font-size: 36px;
                color: {COLORS['fg']};
                margin: 10px 0;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
            }}
            QCheckBox::indicator:unchecked {{
                border: 2px solid {COLORS['fg_faded']};
                background-color: {COLORS['bg_hard']};
                border-radius: 3px;
            }}
            QCheckBox::indicator:checked {{
                border: 2px solid {COLORS['highlight']};
                background-color: {COLORS['highlight']};
                border-radius: 3px;
            }}
            """
        )
        layout.addWidget(self.copy_checkbox)

        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.setStyleSheet(
            f"""
            QPushButton {{
                font-family: {FONT_FAMILY};
                font-size: 36px;
                color: {COLORS['fg']};
                background-color: {COLORS['bg_hard']};
                border: 2px solid {COLORS['fg_faded']};
                border-radius: 5px;
                padding: 8px 16px;
                margin: 5px;
            }}
            QPushButton:hover {{
                color: {COLORS['highlight']};
                border-color: {COLORS['highlight']};
                background-color: {COLORS['bg_soft']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['fg_faded']};
            }}
            """
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def get_file_path(self):
        """Get the selected file path."""
        return self.file_selector.file_input.text()

    def get_copy_option(self):
        """Get whether to copy the file."""
        return self.copy_checkbox.isChecked()


class ManageCardsDialog(QDialog):
    """Dialog for managing cards in a deck."""

    def __init__(self, deck_id, parent=None):
        super().__init__(parent)
        self.deck_id = deck_id
        self.setWindowTitle("Manage Cards")
        self.setModal(True)
        self.setMinimumSize(800, 600)
        self.resize(800, 600)

        # Set dialog styling
        self.setStyleSheet(f"background-color: {COLORS['bg_soft']};")

        layout = QVBoxLayout()

        # Title label
        title_label = QLabel("Cards in Deck")
        title_label.setStyleSheet(
            f"""
            QLabel {{
                font-family: {FONT_FAMILY};
                font-size: 32px;
                font-weight: bold;
                color: {COLORS['fg']};
                margin-bottom: 20px;
            }}
            """
        )
        layout.addWidget(title_label)

        # Cards container with scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(
            f"""
            QScrollArea {{
                border: 2px solid {COLORS['fg_faded']};
                border-radius: 5px;
                background-color: {COLORS['bg_hard']};
            }}
            """
        )

        self.cards_widget = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_widget)
        self.cards_layout.setSpacing(5)
        self.cards_layout.setContentsMargins(10, 10, 10, 10)

        scroll_area.setWidget(self.cards_widget)

        # Load cards
        self.load_cards()

        layout.addWidget(scroll_area)

        self.setLayout(layout)

    def load_cards(self):
        """Load and display all cards in the deck."""
        try:
            # Import Card model here to avoid circular imports
            from pathlib import Path

            from database.database import db
            from database.models import Card

            # Query all cards for this deck
            cards = db.session.query(Card).filter(Card.deck_id == self.deck_id).all()

            if not cards:
                no_cards_label = QLabel("No cards found in this deck.")
                no_cards_label.setStyleSheet(
                    f"""
                    QLabel {{
                        font-family: {FONT_FAMILY};
                        font-size: 24px;
                        color: {COLORS['fg_faded']};
                        padding: 20px;
                        text-align: center;
                    }}
                    """
                )
                self.cards_layout.addWidget(no_cards_label)
                return

            for card in cards:
                # Create card item widget
                card_item = QWidget()
                card_layout = QHBoxLayout(card_item)
                card_layout.setContentsMargins(10, 10, 10, 10)

                # File icon and name
                file_name = Path(card.path).name
                card_info = f"📄 {file_name}"
                if hasattr(card, "created_at") and card.created_at:
                    card_info += (
                        f" (Added: {card.created_at.strftime('%Y-%m-%d %H:%M')})"
                    )

                card_label = QLabel(card_info)
                card_label.setStyleSheet(
                    f"""
                    QLabel {{
                        font-family: {FONT_FAMILY};
                        font-size: 24px;
                        color: {COLORS['fg']};
                        padding: 10px;
                    }}
                    """
                )

                # Delete button with trash icon
                delete_btn = QPushButton()
                delete_btn.setFixedSize(40, 40)

                # Create red trash icon
                red_trash_icon = create_colored_icon(
                    "resources/trash.svg", "#ff4444", 24
                )
                delete_btn.setIcon(red_trash_icon)
                delete_btn.setStyleSheet(
                    f"""
                    QPushButton {{
                        background-color: transparent;
                        border: 2px solid #ff4444;
                        border-radius: 8px;
                        padding: 5px;
                    }}
                    QPushButton:hover {{
                        background-color: #ff4444;
                        border: 2px solid #ff4444;
                    }}
                    QPushButton:pressed {{
                        background-color: #dd3333;
                        border: 2px solid #dd3333;
                    }}
                    """
                )

                # Store card ID in button for deletion
                delete_btn.card_id = card.id
                delete_btn.clicked.connect(
                    lambda checked, btn=delete_btn: self.delete_card(btn.card_id)
                )

                # Add to layout
                card_layout.addWidget(card_label)
                card_layout.addStretch()  # Push delete button to right
                card_layout.addWidget(delete_btn)

                # Style the card item
                card_item.setStyleSheet(
                    f"""
                    QWidget {{
                        background-color: {COLORS['bg_soft']};
                        border: 1px solid {COLORS['fg_faded']};
                        border-radius: 5px;
                        margin: 2px;
                    }}
                    QWidget:hover {{
                        background-color: {COLORS['bg_hard']};
                    }}
                    """
                )

                self.cards_layout.addWidget(card_item)

        except Exception as e:
            error_label = QLabel(f"Error loading cards: {str(e)}")
            error_label.setStyleSheet(
                f"""
                QLabel {{
                    font-family: {FONT_FAMILY};
                    font-size: 24px;
                    color: #ff4444;
                    padding: 20px;
                }}
                """
            )
            self.cards_layout.addWidget(error_label)

    def delete_card(self, card_id):
        """Delete a card from the deck."""
        try:
            # Confirm deletion
            reply = QMessageBox.question(
                self,
                "Delete Card",
                "Are you sure you want to delete this card?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )

            if reply == QMessageBox.Yes:
                # Import here to avoid circular imports
                from database.database import db
                from database.models import Card

                # Delete from database
                card = db.session.query(Card).filter(Card.id == card_id).first()
                if card:
                    db.session.delete(card)
                    db.session.commit()

                    # Refresh the list
                    self.refresh_cards()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete card: {str(e)}")

    def refresh_cards(self):
        """Refresh the cards display."""
        # Clear existing items
        for i in reversed(range(self.cards_layout.count())):
            child = self.cards_layout.itemAt(i).widget()
            if child:
                child.setParent(None)

        # Reload cards
        self.load_cards()
