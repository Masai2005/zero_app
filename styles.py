"""
Styles module for the application.
Contains color schemes and styling for the application components.
"""
from enum import Enum
from PySide6.QtGui import QColor, QPalette, QFont
from PySide6.QtCore import Qt


class Theme(Enum):
    LIGHT = 1
    DARK = 2


class Colors:
    # Light theme colors
    LIGHT_BACKGROUND = "#FFFFFF"
    LIGHT_FOREGROUND = "#333333"
    LIGHT_PRIMARY = "#2196F3"  # Blue
    LIGHT_SECONDARY = "#90CAF9"  # Light Blue
    LIGHT_ACCENT = "#1976D2"  # Dark Blue
    LIGHT_ERROR = "#F44336"
    LIGHT_SUCCESS = "#4CAF50"
    LIGHT_WARNING = "#FFC107"
    LIGHT_INFO = "#2196F3"
    LIGHT_DISABLED = "#BDBDBD"
    LIGHT_CARD = "#F5F5F5"
    LIGHT_BORDER = "#E0E0E0"
    
    # Dark theme colors
    DARK_BACKGROUND = "#121212"
    DARK_FOREGROUND = "#FFFFFF"
    DARK_PRIMARY = "#2196F3"  # Blue
    DARK_SECONDARY = "#1565C0"  # Darker Blue
    DARK_ACCENT = "#64B5F6"  # Light Blue
    DARK_ERROR = "#F44336"
    DARK_SUCCESS = "#4CAF50"
    DARK_WARNING = "#FFC107"
    DARK_INFO = "#2196F3"
    DARK_DISABLED = "#757575"
    DARK_CARD = "#1E1E1E"
    DARK_BORDER = "#333333"


class StyleSheet:
    @staticmethod
    def get_main_style(theme=Theme.LIGHT):
        if theme == Theme.DARK:
            return f"""
            QMainWindow, QDialog {{
                background-color: {Colors.DARK_BACKGROUND};
                color: {Colors.DARK_FOREGROUND};
            }}
            QWidget {{
                background-color: {Colors.DARK_BACKGROUND};
                color: {Colors.DARK_FOREGROUND};
            }}
            QPushButton {{
                background-color: {Colors.DARK_PRIMARY};
                color: {Colors.DARK_FOREGROUND};
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {Colors.DARK_ACCENT};
            }}
            QPushButton:disabled {{
                background-color: {Colors.DARK_DISABLED};
                color: {Colors.DARK_FOREGROUND};
            }}
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
                background-color: {Colors.DARK_CARD};
                color: {Colors.DARK_FOREGROUND};
                border: 1px solid {Colors.DARK_BORDER};
                border-radius: 4px;
                padding: 8px;
            }}
            QLabel {{
                color: {Colors.DARK_FOREGROUND};
            }}
            QTabWidget::pane {{
                border: 1px solid {Colors.DARK_BORDER};
                background-color: {Colors.DARK_CARD};
            }}
            QTabBar::tab {{
                background-color: {Colors.DARK_BACKGROUND};
                color: {Colors.DARK_FOREGROUND};
                padding: 8px 16px;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background-color: {Colors.DARK_PRIMARY};
                color: {Colors.DARK_FOREGROUND};
            }}
            QTableView, QTreeView, QListView {{
                background-color: {Colors.DARK_CARD};
                color: {Colors.DARK_FOREGROUND};
                border: 1px solid {Colors.DARK_BORDER};
                gridline-color: {Colors.DARK_BORDER};
                selection-background-color: {Colors.DARK_PRIMARY};
                selection-color: {Colors.DARK_FOREGROUND};
            }}
            QHeaderView::section {{
                background-color: {Colors.DARK_CARD};
                color: {Colors.DARK_FOREGROUND};
                padding: 4px;
                border: 1px solid {Colors.DARK_BORDER};
            }}
            QScrollBar:vertical, QScrollBar:horizontal {{
                background-color: {Colors.DARK_CARD};
                width: 12px;
                height: 12px;
            }}
            QScrollBar::handle:vertical, QScrollBar::handle:horizontal {{
                background-color: {Colors.DARK_SECONDARY};
                border-radius: 6px;
            }}
            QMenu {{
                background-color: {Colors.DARK_CARD};
                color: {Colors.DARK_FOREGROUND};
                border: 1px solid {Colors.DARK_BORDER};
            }}
            QMenu::item:selected {{
                background-color: {Colors.DARK_PRIMARY};
            }}
            QGroupBox {{
                border: 1px solid {Colors.DARK_BORDER};
                border-radius: 4px;
                margin-top: 16px;
                color: {Colors.DARK_FOREGROUND};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                color: {Colors.DARK_FOREGROUND};
            }}
            """
        else:
            return f"""
            QMainWindow, QDialog {{
                background-color: {Colors.LIGHT_BACKGROUND};
                color: {Colors.LIGHT_FOREGROUND};
            }}
            QWidget {{
                background-color: {Colors.LIGHT_BACKGROUND};
                color: {Colors.LIGHT_FOREGROUND};
            }}
            QPushButton {{
                background-color: {Colors.LIGHT_PRIMARY};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {Colors.LIGHT_ACCENT};
            }}
            QPushButton:disabled {{
                background-color: {Colors.LIGHT_DISABLED};
                color: white;
            }}
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
                background-color: white;
                color: {Colors.LIGHT_FOREGROUND};
                border: 1px solid {Colors.LIGHT_BORDER};
                border-radius: 4px;
                padding: 8px;
            }}
            QLabel {{
                color: {Colors.LIGHT_FOREGROUND};
            }}
            QTabWidget::pane {{
                border: 1px solid {Colors.LIGHT_BORDER};
                background-color: {Colors.LIGHT_BACKGROUND};
            }}
            QTabBar::tab {{
                background-color: {Colors.LIGHT_CARD};
                color: {Colors.LIGHT_FOREGROUND};
                padding: 8px 16px;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background-color: {Colors.LIGHT_PRIMARY};
                color: white;
            }}
            QTableView, QTreeView, QListView {{
                background-color: white;
                color: {Colors.LIGHT_FOREGROUND};
                border: 1px solid {Colors.LIGHT_BORDER};
                gridline-color: {Colors.LIGHT_BORDER};
                selection-background-color: {Colors.LIGHT_PRIMARY};
                selection-color: white;
            }}
            QHeaderView::section {{
                background-color: {Colors.LIGHT_CARD};
                color: {Colors.LIGHT_FOREGROUND};
                padding: 4px;
                border: 1px solid {Colors.LIGHT_BORDER};
            }}
            QScrollBar:vertical, QScrollBar:horizontal {{
                background-color: {Colors.LIGHT_CARD};
                width: 12px;
                height: 12px;
            }}
            QScrollBar::handle:vertical, QScrollBar::handle:horizontal {{
                background-color: {Colors.LIGHT_SECONDARY};
                border-radius: 6px;
            }}
            QMenu {{
                background-color: white;
                color: {Colors.LIGHT_FOREGROUND};
                border: 1px solid {Colors.LIGHT_BORDER};
            }}
            QMenu::item:selected {{
                background-color: {Colors.LIGHT_PRIMARY};
                color: white;
            }}
            QGroupBox {{
                border: 1px solid {Colors.LIGHT_BORDER};
                border-radius: 4px;
                margin-top: 16px;
                color: {Colors.LIGHT_FOREGROUND};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                color: {Colors.LIGHT_FOREGROUND};
            }}
            """

    @staticmethod
    def get_login_style(theme=Theme.LIGHT):
        if theme == Theme.DARK:
            return f"""
            QWidget#loginWidget {{
                background-color: {Colors.DARK_BACKGROUND};
            }}
            QLabel#titleLabel {{
                color: {Colors.DARK_PRIMARY};
                font-size: 24px;
                font-weight: bold;
            }}
            QLineEdit {{
                background-color: {Colors.DARK_CARD};
                color: {Colors.DARK_FOREGROUND};
                border: 1px solid {Colors.DARK_BORDER};
                border-radius: 4px;
                padding: 10px;
                font-size: 14px;
            }}
            QPushButton#loginButton {{
                background-color: {Colors.DARK_PRIMARY};
                color: {Colors.DARK_FOREGROUND};
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton#loginButton:hover {{
                background-color: {Colors.DARK_ACCENT};
            }}
            QPushButton#forgotPasswordButton {{
                background-color: transparent;
                color: {Colors.DARK_PRIMARY};
                border: none;
                font-size: 12px;
                text-decoration: underline;
            }}
            QPushButton#forgotPasswordButton:hover {{
                color: {Colors.DARK_ACCENT};
            }}
            """
        else:
            return f"""
            QWidget#loginWidget {{
                background-color: {Colors.LIGHT_BACKGROUND};
            }}
            QLabel#titleLabel {{
                color: {Colors.LIGHT_PRIMARY};
                font-size: 24px;
                font-weight: bold;
            }}
            QLineEdit {{
                background-color: white;
                color: {Colors.LIGHT_FOREGROUND};
                border: 1px solid {Colors.LIGHT_BORDER};
                border-radius: 4px;
                padding: 10px;
                font-size: 14px;
            }}
            QPushButton#loginButton {{
                background-color: {Colors.LIGHT_PRIMARY};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton#loginButton:hover {{
                background-color: {Colors.LIGHT_ACCENT};
            }}
            QPushButton#forgotPasswordButton {{
                background-color: transparent;
                color: {Colors.LIGHT_PRIMARY};
                border: none;
                font-size: 12px;
                text-decoration: underline;
            }}
            QPushButton#forgotPasswordButton:hover {{
                color: {Colors.LIGHT_ACCENT};
            }}
            """

    @staticmethod
    def get_sidebar_style(theme=Theme.LIGHT):
        if theme == Theme.DARK:
            return f"""
            QWidget#sidebar {{
                background-color: {Colors.DARK_CARD};
                border-right: 1px solid {Colors.DARK_BORDER};
            }}
            QPushButton {{
                background-color: transparent;
                color: {Colors.DARK_FOREGROUND};
                border: none;
                text-align: left;
                padding: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {Colors.DARK_PRIMARY};
            }}
            QPushButton#activeButton {{
                background-color: {Colors.DARK_PRIMARY};
                color: {Colors.DARK_FOREGROUND};
            }}
            QLabel#userLabel {{
                color: {Colors.DARK_PRIMARY};
                font-weight: bold;
                font-size: 14px;
                padding: 10px;
            }}
            """
        else:
            return f"""
            QWidget#sidebar {{
                background-color: {Colors.LIGHT_CARD};
                border-right: 1px solid {Colors.LIGHT_BORDER};
            }}
            QPushButton {{
                background-color: transparent;
                color: {Colors.LIGHT_FOREGROUND};
                border: none;
                text-align: left;
                padding: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {Colors.LIGHT_PRIMARY};
                color: white;
            }}
            QPushButton#activeButton {{
                background-color: {Colors.LIGHT_PRIMARY};
                color: white;
            }}
            QLabel#userLabel {{
                color: {Colors.LIGHT_PRIMARY};
                font-weight: bold;
                font-size: 14px;
                padding: 10px;
            }}
            """


def set_application_palette(app, theme=Theme.LIGHT):
    """Set application color palette based on theme"""
    palette = QPalette()
    
    if theme == Theme.DARK:
        # Dark theme palette
        palette.setColor(QPalette.Window, QColor(Colors.DARK_BACKGROUND))
        palette.setColor(QPalette.WindowText, QColor(Colors.DARK_FOREGROUND))
        palette.setColor(QPalette.Base, QColor(Colors.DARK_CARD))
        palette.setColor(QPalette.AlternateBase, QColor(Colors.DARK_BACKGROUND))
        palette.setColor(QPalette.ToolTipBase, QColor(Colors.DARK_BACKGROUND))
        palette.setColor(QPalette.ToolTipText, QColor(Colors.DARK_FOREGROUND))
        palette.setColor(QPalette.Text, QColor(Colors.DARK_FOREGROUND))
        palette.setColor(QPalette.Button, QColor(Colors.DARK_PRIMARY))
        palette.setColor(QPalette.ButtonText, QColor(Colors.DARK_FOREGROUND))
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(Colors.DARK_ACCENT))
        palette.setColor(QPalette.Highlight, QColor(Colors.DARK_PRIMARY))
        palette.setColor(QPalette.HighlightedText, QColor(Colors.DARK_FOREGROUND))
        palette.setColor(QPalette.Disabled, QPalette.Text, QColor(Colors.DARK_DISABLED))
        palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(Colors.DARK_DISABLED))
    else:
        # Light theme palette
        palette.setColor(QPalette.Window, QColor(Colors.LIGHT_BACKGROUND))
        palette.setColor(QPalette.WindowText, QColor(Colors.LIGHT_FOREGROUND))
        palette.setColor(QPalette.Base, QColor(Colors.LIGHT_BACKGROUND))
        palette.setColor(QPalette.AlternateBase, QColor(Colors.LIGHT_CARD))
        palette.setColor(QPalette.ToolTipBase, QColor(Colors.LIGHT_BACKGROUND))
        palette.setColor(QPalette.ToolTipText, QColor(Colors.LIGHT_FOREGROUND))
        palette.setColor(QPalette.Text, QColor(Colors.LIGHT_FOREGROUND))
        palette.setColor(QPalette.Button, QColor(Colors.LIGHT_PRIMARY))
        palette.setColor(QPalette.ButtonText, QColor("white"))
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(Colors.LIGHT_ACCENT))
        palette.setColor(QPalette.Highlight, QColor(Colors.LIGHT_PRIMARY))
        palette.setColor(QPalette.HighlightedText, QColor("white"))
        palette.setColor(QPalette.Disabled, QPalette.Text, QColor(Colors.LIGHT_DISABLED))
        palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(Colors.LIGHT_DISABLED))
    
    app.setPalette(palette)