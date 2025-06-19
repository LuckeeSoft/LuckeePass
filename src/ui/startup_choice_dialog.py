"""
Startup Choice Dialog
Dialog for users to choose between creating a new vault or restoring from existing data.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QApplication, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QPixmap

from ..utils import apply_custom_title_bar
from src.utils.resource_path import resource_path


class StartupChoiceDialog(QDialog):
    """Dialog for users to choose between creating a new vault or restoring from existing data."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.choice = None  # 'new' or 'restore'
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
        self.resize(300, 300)
        
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
        
        # Choice buttons
        choice_layout = QHBoxLayout()
        choice_layout.setSpacing(15)
        
        # New Vault Option
        new_frame = QFrame()
        new_frame.setFrameStyle(QFrame.NoFrame)
        new_frame.setStyleSheet("background: none; border: none;")
        new_layout = QVBoxLayout(new_frame)
        new_layout.setContentsMargins(0, 0, 0, 0)
        new_layout.setSpacing(2)
        
        # Restore the subtext/description for 'Create New Vault' (but not the heading or background)
        new_desc = QLabel("Start fresh with a new password vault.")
        new_desc.setWordWrap(True)
        new_desc.setStyleSheet("color: #dce6f2; margin-top: 0px; margin-bottom: 8px;")
        new_desc.setAlignment(Qt.AlignCenter)
        new_layout.addWidget(new_desc)
        
        self.new_btn = QPushButton("Create New Vault")
        self.new_btn.clicked.connect(lambda: self.make_choice('new'))
        self.new_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078D7; color: white; border: none;
                padding: 6px 12px; border-radius: 4px; font-weight: bold;
                margin-top: 5px; /* Keep a bit of space below the description */
            }
            QPushButton:hover { background-color: #005B9C; }
        """)
        
        # Add hyperlink-style restore button
        self.restore_link = QPushButton("Restore from existing file")
        self.restore_link.setStyleSheet("QPushButton { color: #60A3D9; background: transparent; border: none; text-decoration: underline; font-size: 12px; margin-top: 8px; } QPushButton:hover { color: #0078D7; }")
        self.restore_link.setCursor(Qt.PointingHandCursor)
        self.restore_link.clicked.connect(lambda: self.make_choice('restore'))
        
        new_layout.addWidget(self.new_btn)
        new_layout.addWidget(self.restore_link, alignment=Qt.AlignHCenter)
        
        choice_layout.addWidget(new_frame, 1)
        
        layout.addLayout(choice_layout)
        layout.addStretch(1)

        self.setLayout(layout)
    
    def make_choice(self, choice):
        """Set the user's choice and close the dialog."""
        self.choice = choice
        self.accept() 