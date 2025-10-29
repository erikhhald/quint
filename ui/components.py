"""
Shared UI components for consistent styling and behavior across pages.
"""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtWidgets import QPushButton

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


def create_floating_back_button(text: str = "", parent=None) -> QPushButton:
    """
    Create a consistently styled back button.

    Args:
        text: Button text (default: "<")
        parent: Parent widget

    Returns:
        Configured QPushButton
    """
    button = QPushButton(text, parent)
    # Create colored icon from SVG
    icon = create_colored_icon("resources/left_arrow.svg", COLORS['highlight'], 24)
    button.setIcon(icon)
    button.setIconSize(button.size())
    button.setStyleSheet(
        f"""
        QPushButton {{
            font-family: {FONT_FAMILY};
            font-size: 16px;
            font-weight: bold;
            color: {COLORS['fg']};
            background-color: {COLORS['bg_hard']};
            border: 2px solid {COLORS['fg_dim']};
            border-radius: 20px;
            padding: 8px 16px;
            min-width: 60px;
            min-height: 40px;
        }}
        QPushButton:hover {{
            background-color: {COLORS['fg_dim']};
            color: {COLORS['bg_hard']};
            border-color: {COLORS['highlight']};
        }}
        QPushButton:pressed {{
            background-color: {COLORS['highlight']};
            color: {COLORS['bg_hard']};
        }}
        """
    )
    # Move the button to top-left corner
    button.move(10, 10)
    button.raise_()  # Bring to front
    return button


def create_back_button(text: str = "", parent=None) -> QPushButton:
    """
    Create a consistently styled back button (non-floating version for compatibility).
    
    Args:
        text: Button text (default: "<")
        parent: Parent widget
        
    Returns:
        Configured QPushButton
    """
    return create_floating_back_button(text, parent)


def create_navigation_back_button(text: str = "← Back", parent=None) -> QPushButton:
    """
    Create a back button with arrow for navigation (used in chat page).

    Args:
        text: Button text (default: "← Back")
        parent: Parent widget

    Returns:
        Configured QPushButton
    """
    return create_back_button(text, parent)


def create_title_label(text: str, parent=None, icon_path: str = None):
    """
    Create a consistently styled title label.

    Args:
        text: Title text
        parent: Parent widget
        icon_path: Optional path to icon file

    Returns:
        Configured QLabel or QHBoxLayout with icon
    """
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QPixmap, QIcon
    from PyQt5.QtWidgets import QLabel, QHBoxLayout, QWidget

    if icon_path:
        # Create container widget with horizontal layout for icon + text
        container = QWidget(parent)
        layout = QHBoxLayout(container)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(15)
        
        # Icon label
        icon_label = QLabel()
        # Create colored icon and convert to pixmap
        colored_icon = create_colored_icon(icon_path, COLORS['highlight'], 40)
        pixmap = colored_icon.pixmap(40, 40)
        if not pixmap.isNull():
            icon_label.setPixmap(pixmap)
        layout.addWidget(icon_label)
        
        # Text label
        text_label = QLabel(text)
        text_label.setAlignment(Qt.AlignCenter)
        text_label.setStyleSheet(
            f"font-family: monospace; font-size: 36px; color: {COLORS['fg']}; margin-bottom: 20px;"
        )
        layout.addWidget(text_label)
        
        return container
    else:
        label = QLabel(text, parent)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet(
            f"font-family: monospace; font-size: 36px; color: {COLORS['fg']}; margin-bottom: 20px;"
        )
        return label

