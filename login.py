"""
Login window module for the application.
"""
import sys
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QDialog,
    QFormLayout
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPixmap, QIcon

from styles import StyleSheet, Theme
from utils import UserManager, show_message, AppSettings, handle_data_error


class ForgotPasswordDialog(QDialog):
    """Dialog for password reset"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Forgot Password")
        self.setMinimumWidth(300)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout()
        
        # Form layout for inputs
        form_layout = QFormLayout()
        
        # Username field
        self.username_input = QLineEdit()
        form_layout.addRow("Username:", self.username_input)
        
        # New password field
        self.new_password_input = QLineEdit()
        self.new_password_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow("New Password:", self.new_password_input)
        
        # Confirm password field
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Confirm Password:", self.confirm_password_input)
        
        layout.addLayout(form_layout)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Reset button
        self.reset_button = QPushButton("Reset Password")
        self.reset_button.clicked.connect(self.reset_password)
        
        # Cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.reset_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def reset_password(self):
        """Handle password reset"""
        username = self.username_input.text().strip()
        new_password = self.new_password_input.text().strip()
        confirm_password = self.confirm_password_input.text().strip()
        
        # Validate inputs
        if not username:
            show_message(self, "Error", "Please enter a username", QMessageBox.Warning)
            return
        
        if not new_password:
            show_message(self, "Error", "Please enter a new password", QMessageBox.Warning)
            return
        
        if new_password != confirm_password:
            show_message(self, "Error", "Passwords do not match", QMessageBox.Warning)
            return
        
        # Reset password
        success, message = UserManager.reset_password(username, new_password)
        
        if success:
            show_message(self, "Success", message)
            self.accept()
        else:
            show_message(self, "Error", message, QMessageBox.Warning)


class LoginWindow(QWidget):
    """Login window for user authentication"""
    
    # Signal to emit when login is successful
    login_successful = Signal(dict)
    
    def __init__(self, theme=Theme.LIGHT):
        super().__init__()
        self.theme = theme
        self.app_settings = AppSettings()
        
        # Setup window properties
        self.setWindowTitle("ZERO - Login")
        self.setFixedSize(400, 500)
        self.setObjectName("loginWidget")
        
        # Set window stylesheet
        self.setStyleSheet(StyleSheet.get_login_style(self.theme))
        
        # Setup UI components
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI components"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)
        
        # Logo section
        logo_layout = QHBoxLayout()
        logo_label = QLabel()
        # logo_pixmap = QPixmap("/images/Logo.jpg")
        # logo_label.setPixmap(logo_pixmap.scaled(QSize(100, 100), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo_layout.addWidget(logo_label, alignment=Qt.AlignCenter)
        main_layout.addLayout(logo_layout)
        
        # Title section
        title_label = QLabel("ZERO")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Add some spacing
        main_layout.addSpacing(20)
        
        # Username section
        username_label = QLabel("Username")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        main_layout.addWidget(username_label)
        main_layout.addWidget(self.username_input)
        
        # Password section
        password_label = QLabel("Password")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.returnPressed.connect(self.login)
        main_layout.addWidget(password_label)
        main_layout.addWidget(self.password_input)
        
        # Login button
        self.login_button = QPushButton("Login")
        self.login_button.setObjectName("loginButton")
        self.login_button.clicked.connect(self.login)
        main_layout.addWidget(self.login_button)
        
        # Forgot password button
        self.forgot_password_button = QPushButton("Forgot Password?")
        self.forgot_password_button.setObjectName("forgotPasswordButton")
        self.forgot_password_button.clicked.connect(self.show_forgot_password)
        main_layout.addWidget(self.forgot_password_button, alignment=Qt.AlignCenter)
        
        # Add stretch to push everything to the top
        main_layout.addStretch()
        
        # Set the layout
        self.setLayout(main_layout)
        
        # Pre-fill last username
        last_user = self.app_settings.get_last_user()
        if last_user:
            self.username_input.setText(last_user)
            self.password_input.setFocus()
    
    def login(self):
        """Handle login attempt"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            show_message(self, "Error", "Please enter both username and password", QMessageBox.Warning)
            return
        
        user = UserManager.authenticate(username, password)
        
        if user:
            # Save last logged in user
            self.app_settings.set_last_user(username)
            
            # Emit signal with user data
            self.login_successful.emit(user)
        else:
            show_message(self, "Error", "Invalid username or password", QMessageBox.Warning)
    
    def show_forgot_password(self):
        """Show forgot password dialog"""
        dialog = ForgotPasswordDialog(self)
        dialog.exec()