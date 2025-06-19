"""
Welcome Dialog
Dialog for first-time users to set up their master password.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QMessageBox, QFrame, QApplication
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QPixmap

from ..core import UserManager
from ..utils import apply_custom_title_bar
from src.utils.resource_path import resource_path


class WelcomeDialog(QDialog):
    """Dialog for first-time users to set up their account."""
    
    def __init__(self, user_manager: UserManager, parent=None):
        super().__init__(parent)
        self.user_manager = user_manager
        self.master_password = ""
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
        # Apply custom title bar when shown
        QTimer.singleShot(100, self.customize_title_bar)
    
    def setup_ui(self):
        """Setup the user interface."""
        self.setWindowTitle("Welcome to LuckeePass")
        self.setModal(True)
        self.resize(400, 300)
        
        layout = QVBoxLayout()
        
        # Logo
        self.logo_label = QLabel()
        pixmap = QPixmap(resource_path("images/luckeepasslogo.png"))
        if not pixmap.isNull():
            self.logo_label.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.logo_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(self.logo_label)

        # Welcome header
        welcome_label = QLabel("Welcome to LuckeePass!")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setFont(QFont("Jua", 18, QFont.Bold))
        welcome_label.setStyleSheet("color: #60A3D9; margin: 10px;")
        layout.addWidget(welcome_label)
        
        # Welcome message
        message_label = QLabel(
            "You're about to create your secure password vault. "
            "This will be your first and last line of defense for all your passwords and secure notes."
        )
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("margin: 10px; padding: 10px; background-color: #243447; border-radius: 5px;")
        layout.addWidget(message_label)
        
        # Master Password
        self.master_password_label = QLabel("Master Password:")
        layout.addWidget(self.master_password_label)
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("Enter your master password (minimum 6 characters)")
        layout.addWidget(self.password_edit)
        
        # Confirm Password
        self.confirm_password_label = QLabel("Confirm Master Password:")
        layout.addWidget(self.confirm_password_label)
        self.confirm_password_edit = QLineEdit()
        self.confirm_password_edit.setEchoMode(QLineEdit.Password)
        self.confirm_password_edit.setPlaceholderText("Confirm your master password")
        layout.addWidget(self.confirm_password_edit)

        # Buttons
        button_layout = QHBoxLayout()
        
        self.setup_btn = QPushButton("Complete Setup")
        self.setup_btn.clicked.connect(self.handle_setup)
        self.setup_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078D7; color: white; border: none;
                padding: 10px 20px; border-radius: 4px; font-weight: bold;
            }
            QPushButton:hover { background-color: #005B9C; }
        """)
        button_layout.addWidget(self.setup_btn)

        layout.addLayout(button_layout)
        layout.addStretch(1)

        self.setLayout(layout)
        
        # Connect enter key
        self.password_edit.returnPressed.connect(self.handle_setup)
        self.confirm_password_edit.returnPressed.connect(self.handle_setup)
    
    def handle_setup(self):
        """Handle the master password setup."""
        password = self.password_edit.text()
        confirm_password = self.confirm_password_edit.text()

        # Validation
        if not password or not confirm_password:
            QMessageBox.warning(self, "Missing Information", "Please enter and confirm your master password.")
            return
        
        if password != confirm_password:
            QMessageBox.warning(self, "Password Mismatch", "Passwords do not match. Please try again.")
            self.confirm_password_edit.clear()
            return
        
        if len(password) < 6:
            QMessageBox.warning(self, "Weak Password", "Master password must be at least 6 characters long.")
            return

        try:
            self.user_manager.set_master_password(password)
            self.master_password = password
            
            QMessageBox.information(self, "Setup Complete!", "Your master password has been set successfully. You can now start using LuckeePass!")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Setup Failed", f"Failed to set master password: {str(e)}") 