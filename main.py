"""
Main entry point for the ZERO application.
"""
import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon, QFontDatabase
from PySide6.QtCore import Qt

from utils import DataManager, AppSettings
from styles import Theme, set_application_palette
from login import LoginWindow
from dashboard import Dashboard


class ZeroApplication:
    """Main application class"""
    
    def __init__(self):
        # Create data directory and initialize files if they don't exist
        try:
            DataManager.init_data_files()
        except Exception as e:
            print(f"Critical error during initialization: {e}")
            sys.exit(1)
        
        # Create application
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("ZERO")
        self.app.setApplicationVersion("1.0.0")
        
        # Load settings
        self.app_settings = AppSettings()
        self.theme = Theme.DARK if self.app_settings.get_theme() == "dark" else Theme.LIGHT
        
        # Set application style
        set_application_palette(self.app, self.theme)
        
        # Show login window
        self.show_login()
        
        # Execute application
        sys.exit(self.app.exec())
    
    def show_login(self):
        """Show login window"""
        self.login_window = LoginWindow(self.theme)
        self.login_window.login_successful.connect(self.show_dashboard)
        self.login_window.show()
    
    def show_dashboard(self, user_data):
        """Show dashboard window"""
        self.dashboard = Dashboard(user_data, self.theme)
        self.dashboard.logout_signal.connect(self.logout)
        self.dashboard.show()
        self.login_window.hide()
    
    def logout(self):
        """Handle logout"""
        self.dashboard.close()
        self.show_login()


if __name__ == "__main__":
    ZeroApplication()