"""
Shared UI components for consistent styling and behavior across pages.
"""

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QIcon, QPainter, QPixmap
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QWidget,
)

from .theme import COLORS, FONT_FAMILY


def create_colored_icon(svg_path: str, color: str, size: int = 24) -> QIcon:
    """
    Create a colored icon from an SVG file.

    Args:
        svg_path: Path to SVG file
        color: Hex color string (e.g., "#e78a4e")
        size: Icon size in pixels

    Returns:
        QIcon with the specified color
    """
    # Create a pixmap with the desired size
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    # Render SVG to pixmap
    renderer = QSvgRenderer(svg_path)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()

    # Apply color overlay
    colored_pixmap = QPixmap(size, size)
    colored_pixmap.fill(Qt.transparent)
    painter = QPainter(colored_pixmap)
    painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
    painter.drawPixmap(0, 0, pixmap)
    painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
    painter.fillRect(colored_pixmap.rect(), QColor(color))
    painter.end()

    return QIcon(colored_pixmap)


class BackButton(QPushButton):
    """
    A consistently styled back button with hover effects.
    """

    def __init__(self, text: str = "", parent=None, floating=True):
        super().__init__(text, parent)
        self.floating = floating
        self.setup_ui()

    def setup_ui(self):
        # Create two different colored icons for normal and hover states
        self.orange_icon = create_colored_icon(
            "resources/left_arrow.svg", "#ff6b35", 24
        )
        self.bg_icon = create_colored_icon(
            "resources/left_arrow.svg", COLORS["bg_soft"], 24
        )

        self.setIcon(self.orange_icon)
        self.setIconSize(self.size())

        self.setStyleSheet(
            f"""
            QPushButton {{
                font-family: {FONT_FAMILY};
                font-size: 16px;
                font-weight: bold;
                color: #ff6b35;
                background-color: transparent;
                border: none;
                border-radius: 20px;
                padding: 8px 16px;
                min-width: 60px;
                min-height: 40px;
            }}
            QPushButton:hover {{
                background-color: #ff6b35;
                color: {COLORS['bg_soft']};
                border: 2px solid #ff6b35;
            }}
            QPushButton:pressed {{
                background-color: #e55a2b;
                color: {COLORS['bg_soft']};
                border: 2px solid #e55a2b;
            }}
            """
        )

        if self.floating:
            # Move the button to top-left corner
            self.move(10, 10)
            self.raise_()  # Bring to front

    def enterEvent(self, event):
        self.setIcon(self.bg_icon)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setIcon(self.orange_icon)
        super().leaveEvent(event)


class TitleLabel(QWidget):
    """
    A consistently styled title label with optional icon.
    """

    def __init__(self, text: str, parent=None, icon_path: str = None):
        super().__init__(parent)
        self.text = text
        self.icon_path = icon_path
        self.setup_ui()

    def setup_ui(self):
        if self.icon_path:
            # Create horizontal layout for icon + text
            layout = QHBoxLayout(self)
            layout.setAlignment(Qt.AlignCenter)
            layout.setSpacing(15)

            # Icon label
            icon_label = QLabel()
            colored_icon = create_colored_icon(self.icon_path, COLORS["highlight"], 40)
            pixmap = colored_icon.pixmap(40, 40)
            if not pixmap.isNull():
                icon_label.setPixmap(pixmap)
            layout.addWidget(icon_label)

            # Text label
            text_label = QLabel(self.text)
            text_label.setAlignment(Qt.AlignCenter)
            text_label.setStyleSheet(
                f"font-family: monospace; font-size: 36px; color: {COLORS['fg']}; margin-bottom: 20px;"
            )
            layout.addWidget(text_label)
        else:
            # Simple text label
            layout = QHBoxLayout(self)
            layout.setAlignment(Qt.AlignCenter)

            label = QLabel(self.text)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet(
                f"font-family: monospace; font-size: 36px; color: {COLORS['fg']}; margin-bottom: 20px;"
            )
            layout.addWidget(label)

    def setText(self, text: str):
        """Update the title text."""
        self.text = text
        # Clear and rebuild UI
        for i in reversed(range(self.layout().count())):
            self.layout().itemAt(i).widget().setParent(None)
        self.setup_ui()


class FileSelector(QWidget):
    """
    A file selector widget with input field and browse button.
    """

    fileSelected = pyqtSignal(str)  # Signal emitted when file is selected

    def __init__(self, path_type="file", parent=None):
        super().__init__(parent)

        # Validate path_type
        if path_type not in ("file", "folder"):
            raise ValueError("path_type must be 'file' or 'folder'")

        self.path_type = path_type

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # File path input
        self.file_input = QLineEdit()
        placeholder_text = f"{path_type.capitalize()} path..."
        self.file_input.setPlaceholderText(placeholder_text)
        self.file_input.setStyleSheet(
            f"""
            QLineEdit {{
                font-family: {FONT_FAMILY};
                font-size: 16px;
                color: {COLORS['fg']};
                background-color: {COLORS['bg_hard']};
                border: 2px solid {COLORS['fg_faded']};
                border-radius: 5px;
                padding: 8px;
                min-width: 300px;
            }}
            QLineEdit:focus {{
                border-color: {COLORS['highlight']};
            }}
        """
        )

        # Browse button with appropriate icon
        if path_type == "file":
            icon_path = "resources/file.svg"
        else:  # folder
            icon_path = "resources/folder.svg"

        icon = create_colored_icon(icon_path, COLORS["fg"], 24)
        self.browse_button = QPushButton()
        self.browse_button.setIcon(icon)
        self.browse_button.setFixedSize(40, 40)
        self.browse_button.setStyleSheet(
            f"""
            QPushButton {{
                font-family: {FONT_FAMILY};
                font-size: 18px;
                color: {COLORS['fg']};
                background-color: {COLORS['bg_hard']};
                border: 2px solid {COLORS['fg_faded']};
                border-radius: 5px;
                margin-left: 5px;
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
        self.browse_button.clicked.connect(self.open_file_dialog)

        layout.addWidget(self.file_input)
        layout.addWidget(self.browse_button)

    def open_file_dialog(self):
        """Open file dialog to select a file or folder."""
        if self.path_type == "file":
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Select File", self.file_input.text() or "", "All Files (*)"
            )
        else:  # folder
            file_path = QFileDialog.getExistingDirectory(
                self,
                "Select Folder",
                self.file_input.text() or "",
                QFileDialog.ShowDirsOnly,
            )

        if file_path:
            self.file_input.setText(file_path)
            self.fileSelected.emit(file_path)
