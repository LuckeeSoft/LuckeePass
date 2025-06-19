"""
Login Dialog
Dialog for user login and registration.
"""

import sys
import random
from datetime import datetime
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QMessageBox, QInputDialog
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QCursor, QPixmap, QFontDatabase, QPalette, QColor
from PySide6.QtWidgets import QApplication

from ..core import UserManager
from .welcome_dialog import WelcomeDialog
from src.utils.resource_path import resource_path


class LoginDialog(QDialog):
    """Dialog for user login and registration."""
    
    def __init__(self, user_manager: UserManager, parent=None):
        super().__init__(parent)
        self.user_manager = user_manager
        self.master_password = ""
        self.is_new_user = False
        # Ensure the dialog is a top-level window
        self.setWindowFlags(self.windowFlags() | Qt.Window)
        # Set a dark palette for the dialog
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(20, 30, 48))
        palette.setColor(QPalette.WindowText, QColor(236, 240, 241))
        self.setPalette(palette)
        # Use the Fusion style for better dark mode support
        QApplication.setStyle("Fusion")
        # Initialize status_label here to guarantee its existence
        self.status_label = QLabel("")
        
        self.setup_ui()
        # Apply custom title bar after setup
        QTimer.singleShot(100, self.customize_title_bar)
        # Center the dialog on the screen
        qr = self.frameGeometry()
        cp = QApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    
    def customize_title_bar(self):
        """Apply custom title bar styling using Windows API."""
        apply_custom_title_bar(self)
    
    def showEvent(self, event):
        super().showEvent(event)
        # Apply custom title bar when shown and ensure initial state is set after UI is visible
        QTimer.singleShot(100, self.customize_title_bar)
        QTimer.singleShot(100, self.show_login_state) # Call after short delay to ensure UI is ready
    
    def setup_ui(self):
        """Setup the user interface."""
        # Add font to QFontDatabase
        QFontDatabase.addApplicationFont("Jua-Regular.ttf")

        self.setWindowTitle("LuckeePass - Login")
        self.setModal(True)
        self.setFixedWidth(400)
        self.resize(400, 300)
        
        layout = QVBoxLayout()
        
        # Configure status_label (already initialized in __init__)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: red;")
        layout.addWidget(self.status_label)
        
        # Logo
        self.logo_label = QLabel()
        self.logo_label.setMinimumHeight(110)
        pixmap = QPixmap(resource_path("images/luckeepasslogo.png"))
        if not pixmap.isNull():
            self.logo_label.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.logo_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(self.logo_label)

        layout.addStretch(1)  # Add vertical spacer below logo

        # Greeting
        self.greeting_label = QLabel()
        self.greeting_label.setAlignment(Qt.AlignCenter)
        self.greeting_label.setWordWrap(True)
        self.greeting_label.setFont(QFont("Jua", 16, QFont.Bold))
        self.greeting_label.setStyleSheet("color: #60A3D9; margin: 0 10px 10px 10px;")
        self.update_greeting()
        layout.addWidget(self.greeting_label)

        # Master Password
        layout.addWidget(QLabel("Master Password:"))
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("Enter your master password")
        layout.addWidget(self.password_edit)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.login_btn = QPushButton("Login")
        self.login_btn.clicked.connect(self.try_login)
        button_layout.addWidget(self.login_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Connect enter key
        self.password_edit.returnPressed.connect(self.try_login)

    def show_login_state(self):
        """Configure dialog for login (master password already set)."""
        self.setWindowTitle("LuckeePass - Login")
        self.status_label.setText("")
        
        self.login_btn.setText("Login")
        try: self.login_btn.clicked.disconnect() 
        except TypeError: pass # Ignore if no connection exists
        self.login_btn.clicked.connect(self.try_login)

    def try_login(self):
        """Attempt to login with current master password."""
        master_password = self.password_edit.text()
        
        if not master_password:
            self.status_label.setText("Please enter your master password")
            return
        
        if self.user_manager.verify_master_password(master_password):
            self.master_password = master_password
            self.accept()
        else:
            self.status_label.setText("Invalid master password")
            self.password_edit.clear()  # Clear for security 

    def update_greeting(self):
        """Update the greeting label with a time-appropriate message."""
        current_time = datetime.now().strftime('%H:%M')
        greeting = self.get_random_greeting(current_time)
        self.greeting_label.setText(greeting)

    def get_greeting_based_on_time(self, current_time):
        """Determine a greeting based on the current time."""
        hour = int(current_time.split(':')[0])
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 18:
            return "afternoon"
        else:
            return "evening"
    
    def get_random_greeting(self, current_time):
        """Get a random greeting based on the time of day."""
        hour = int(current_time.split(':')[0])
        
        if 5 <= hour < 12:
            greetings = [
                "Good morning! ☀️",
                "Rise and shine! 🌅",
                "Morning vibes! 🌞",
                "Good morning, ready to secure your day? 🔐",
                "Welcome to a new day! ✨",
                "Morning security check! 🛡️",
                "Good morning, let's keep it safe! 🔒",
                "Rise and secure! 🌅"
            ]
        elif 12 <= hour < 18:
            greetings = [
                "Good afternoon! 🌤️",
                "Afternoon security! 🛡️",
                "Good afternoon, staying secure? 🔐",
                "Afternoon vibes! ☀️",
                "Welcome back! 🔒",
                "Afternoon check-in! ✨",
                "Good afternoon, ready to protect? 🛡️",
                "Secure afternoon! 🔐"
            ]
        else:
            greetings = [
                "Good evening! 🌙",
                "Evening security! 🛡️",
                "Good evening, time to secure! 🔐",
                "Evening vibes! 🌆",
                "Welcome to the evening! ✨",
                "Evening check-in! 🔒",
                "Good evening, staying protected? 🛡️",
                "Secure evening! 🌙"
            ]
        
        return random.choice(greetings) 