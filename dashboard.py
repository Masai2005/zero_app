"""
Dashboard module for the application.
The main window after login, contains sidebar and content area.
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QStackedWidget, QSplitter,
    QFrame, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon

from styles import StyleSheet, Theme, Colors
from utils import USER_TYPE_ADMIN, USER_TYPE_SALESMAN
import sales
import notifications
import expenses
import crm
import inventory


class SidebarButton(QPushButton):
    """Custom button for sidebar navigation"""
    
    def __init__(self, text, icon_path=None, parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(50)
        self.setIconSize(QSize(24, 24))
        if icon_path:
            self.setIcon(QIcon(icon_path))


class Sidebar(QWidget):
    """Sidebar widget for navigation"""
    
    # Signal to emit when a button is clicked
    button_clicked = Signal(str)
    
    def __init__(self, user_data, theme=Theme.LIGHT):
        super().__init__()
        self.user_data = user_data
        self.theme = theme
        
        self.setObjectName("sidebar")
        self.setMinimumWidth(200)
        self.setMaximumWidth(250)
        self.setStyleSheet(StyleSheet.get_sidebar_style(self.theme))
        
        # Setup UI components
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # User label
        user_label = QLabel(f"User: {self.user_data.get('name', '')}")
        user_label.setObjectName("userLabel")
        user_label.setAlignment(Qt.AlignCenter)
        user_label.setMinimumHeight(50)
        layout.addWidget(user_label)
        
        # Add a separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)
        
        # Sales button
        self.sales_btn = SidebarButton("Sales")
        self.sales_btn.clicked.connect(lambda: self.button_clicked.emit("sales"))
        layout.addWidget(self.sales_btn)
        
        # Notifications button
        self.notifications_btn = SidebarButton("Notifications")
        self.notifications_btn.clicked.connect(lambda: self.button_clicked.emit("notifications"))
        layout.addWidget(self.notifications_btn)
        
        # Expenses button
        self.expenses_btn = SidebarButton("Expenses")
        self.expenses_btn.clicked.connect(lambda: self.button_clicked.emit("expenses"))
        layout.addWidget(self.expenses_btn)
        
        # Admin-specific buttons
        if self.user_data.get("type") == USER_TYPE_ADMIN:
            # CRM button
            self.crm_btn = SidebarButton("CRM")
            self.crm_btn.clicked.connect(lambda: self.button_clicked.emit("crm"))
            layout.addWidget(self.crm_btn)
            
            # Inventory button  
            self.inventory_btn = SidebarButton("Inventory")
            self.inventory_btn.clicked.connect(lambda: self.button_clicked.emit("inventory"))
            layout.addWidget(self.inventory_btn)        # Add spacer to push buttons to the top
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Settings button
        self.settings_btn = SidebarButton("Settings")
        self.settings_btn.clicked.connect(lambda: self.button_clicked.emit("settings"))
        layout.addWidget(self.settings_btn)
        
        # Logout button
        self.logout_btn = SidebarButton("Logout")
        self.logout_btn.clicked.connect(lambda: self.button_clicked.emit("logout"))
        layout.addWidget(self.logout_btn)
        
        self.setLayout(layout)
    
    def set_active_button(self, button_name):
        """Set active button by name"""
        # Reset all buttons to inactive style
        for btn in self.findChildren(SidebarButton):
            btn.setObjectName("")
            btn.setStyleSheet("")
        
        # Set the selected button as active
        button_map = {
            "sales": self.sales_btn,
            "notifications": self.notifications_btn,
            "expenses": self.expenses_btn,
            "settings": self.settings_btn,
            "logout": self.logout_btn
        }
        
        if self.user_data.get("type") == USER_TYPE_ADMIN:
            button_map.update({
                "crm": self.crm_btn,
                "inventory": self.inventory_btn
            })
        
        if button_name in button_map:
            button_map[button_name].setObjectName("activeButton")
            button_map[button_name].style().polish(button_map[button_name])


class Dashboard(QMainWindow):
    """Main dashboard window"""
    
    # Signal to emit when logout is clicked
    logout_signal = Signal()
    
    def __init__(self, user_data, theme=Theme.LIGHT):
        super().__init__()
        self.user_data = user_data
        self.theme = theme
        
        # Setup window properties
        self.setWindowTitle("ZERO - Dashboard")
        self.setMinimumSize(1000, 600)
        
        # Set window stylesheet
        self.setStyleSheet(StyleSheet.get_main_style(self.theme))
        
        # Setup UI components
        self.setup_ui()
        
        # Initialize to the sales page
        self.sidebar.set_active_button("sales")
        self.show_page("sales")
    
    def setup_ui(self):
        """Setup UI components"""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create sidebar
        self.sidebar = Sidebar(self.user_data, self.theme)
        self.sidebar.button_clicked.connect(self.handle_sidebar_button)
        
        # Create content area
        self.content_area = QStackedWidget()
        
        # Create pages
        self.create_pages()
        
        # Add widgets to main layout
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.content_area)
        
        central_widget.setLayout(main_layout)
    
    def create_pages(self):
        """Create all pages for the content area"""
        # Sales page
        self.sales_page = sales.SalesWindow(self.user_data, self.theme)
        self.content_area.addWidget(self.sales_page)
        
        # Notifications page
        self.notifications_page = notifications.NotificationsWindow(self.user_data, self.theme)
        self.content_area.addWidget(self.notifications_page)
        
        # Expenses page
        self.expenses_page = expenses.ExpensesWindow(self.user_data, self.theme)
        self.content_area.addWidget(self.expenses_page)
        
        # Admin-specific pages
        if self.user_data.get("type") == USER_TYPE_ADMIN:
            # CRM page
            self.crm_page = crm.CRMWindow(self.user_data, self.theme)
            self.content_area.addWidget(self.crm_page)
            
            # Inventory page
            self.inventory_page = inventory.InventoryWindow(self.user_data, self.theme)
            self.content_area.addWidget(self.inventory_page)
        
        # Settings page
        self.settings_page = SettingsWindow(self.theme)
        self.settings_page.theme_changed.connect(self.change_theme)
        self.content_area.addWidget(self.settings_page)
    
    def handle_sidebar_button(self, button_name):
        """Handle sidebar button click"""
        if button_name == "logout":
            self.logout_signal.emit()
        else:
            self.show_page(button_name)
            self.sidebar.set_active_button(button_name)
    
    def show_page(self, page_name):
        """Show the page with the given name"""
        page_map = {
            "sales": 0,
            "notifications": 1,
            "expenses": 2,
        }
        
        # Adjust indices for admin pages
        if self.user_data.get("type") == USER_TYPE_ADMIN:
            page_map.update({
                "crm": 3,
                "inventory": 4,
                "settings": 5
            })
        else:
            page_map.update({
                "settings": 3
            })
        
        if page_name in page_map:
            self.content_area.setCurrentIndex(page_map[page_name])
    
    def change_theme(self, theme):
        """Change the theme of the application"""
        self.theme = Theme.DARK if theme == "dark" else Theme.LIGHT
        
        # Update stylesheets
        self.setStyleSheet(StyleSheet.get_main_style(self.theme))
        self.sidebar.setStyleSheet(StyleSheet.get_sidebar_style(self.theme))
        
        # Update pages
        for i in range(self.content_area.count()):
            page = self.content_area.widget(i)
            if hasattr(page, 'update_theme'):
                page.update_theme(self.theme)


class SettingsWindow(QWidget):
    """Settings page widget"""
    
    # Signal to emit when theme is changed
    theme_changed = Signal(str)
    
    def __init__(self, theme=Theme.LIGHT):
        super().__init__()
        self.theme = theme
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("Settings")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)
        
        # Theme section
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Theme:")
        
        self.light_theme_btn = QPushButton("Light")
        self.light_theme_btn.clicked.connect(lambda: self.change_theme("light"))
        
        self.dark_theme_btn = QPushButton("Dark")
        self.dark_theme_btn.clicked.connect(lambda: self.change_theme("dark"))
        
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.light_theme_btn)
        theme_layout.addWidget(self.dark_theme_btn)
        theme_layout.addStretch()
        
        layout.addLayout(theme_layout)
        
        # Add stretch to push everything to the top
        layout.addStretch()
        
        self.setLayout(layout)
    
    def change_theme(self, theme):
        """Change the theme"""
        self.theme_changed.emit(theme)
    
    def update_theme(self, theme):
        """Update the theme"""
        self.theme = theme