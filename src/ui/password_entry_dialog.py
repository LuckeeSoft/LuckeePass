"""
Password Entry Dialog
Dialog for adding/editing password entries.
"""

from typing import Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QCheckBox, QTextEdit, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer

from ..models import PasswordEntry
from .password_generator_dialog import PasswordGeneratorDialog
from .file_attachment_widget import FileAttachmentWidget
from ..utils import apply_custom_title_bar


class PasswordEntryDialog(QDialog):
    """Dialog for adding/editing password entries."""
    
    def __init__(self, entry: Optional[PasswordEntry] = None, parent=None):
        super().__init__(parent)
        self.entry = entry
        self.setup_ui()
        if entry:
            self.load_entry(entry)
        # Apply custom title bar after setup
        QTimer.singleShot(100, self.customize_title_bar)
    
    def customize_title_bar(self):
        """Apply custom title bar styling using Windows API."""
        apply_custom_title_bar(self)
    
    def showEvent(self, event):
        super().showEvent(event)
        # Apply custom title bar when shown
        QTimer.singleShot(100, self.customize_title_bar)
    
    def setup_ui(self):
        """Setup the user interface."""
        self.setWindowTitle("Password Entry")
        self.setModal(True)
        self.resize(450, 500)  # Increased height to accommodate file attachments
        
        layout = QVBoxLayout()
        
        # Title
        layout.addWidget(QLabel("Title:"))
        self.title_edit = QLineEdit()
        layout.addWidget(self.title_edit)
        
        # Username
        layout.addWidget(QLabel("Username:"))
        self.username_edit = QLineEdit()
        layout.addWidget(self.username_edit)
        
        # Password
        password_layout = QHBoxLayout()
        password_layout.addWidget(QLabel("Password:"))
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(self.password_edit)
        
        self.show_password_cb = QCheckBox("Show")
        self.show_password_cb.toggled.connect(self.toggle_password_visibility)
        password_layout.addWidget(self.show_password_cb)
        
        self.generate_btn = QPushButton("Generate")
        self.generate_btn.clicked.connect(self.generate_password)
        password_layout.addWidget(self.generate_btn)
        
        layout.addLayout(password_layout)
        
        # URL
        layout.addWidget(QLabel("URL:"))
        self.url_edit = QLineEdit()
        layout.addWidget(self.url_edit)
        
        # Category
        layout.addWidget(QLabel("Category:"))
        self.category_edit = QLineEdit()
        layout.addWidget(self.category_edit)
        
        # Notes
        layout.addWidget(QLabel("Notes:"))
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(80)
        layout.addWidget(self.notes_edit)
        
        # File Attachments
        self.file_attachment_widget = FileAttachmentWidget()
        layout.addWidget(self.file_attachment_widget)
        
        # Favorite Checkbox
        self.favorite_checkbox = QCheckBox("Favorite")
        layout.addWidget(self.favorite_checkbox)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.accept)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078D7; color: white; border: none;
                padding: 10px 20px; border-radius: 4px; font-weight: bold;
            }
            QPushButton:hover { background-color: #005B9C; }
        """)
        self.save_btn.setMinimumHeight(36)
        self.save_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        button_layout.addWidget(self.save_btn)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #6C757D; color: white; border: none;
                padding: 10px 20px; border-radius: 4px; font-weight: bold;
            }
            QPushButton:hover { background-color: #545B62; }
        """)
        self.cancel_btn.setMinimumHeight(36)
        self.cancel_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        button_layout.addWidget(self.cancel_btn)

        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def toggle_password_visibility(self, show: bool):
        """Toggle password visibility."""
        if show:
            self.password_edit.setEchoMode(QLineEdit.Normal)
        else:
            self.password_edit.setEchoMode(QLineEdit.Password)
    
    def generate_password(self):
        """Open password generator dialog."""
        dialog = PasswordGeneratorDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.password_edit.setText(dialog.generated_password)
    
    def load_entry(self, entry: PasswordEntry):
        """Load entry data into form."""
        self.title_edit.setText(entry.title)
        self.username_edit.setText(entry.username)
        self.password_edit.setText(entry.password)
        self.url_edit.setText(entry.url)
        self.category_edit.setText(entry.category)
        self.notes_edit.setPlainText(entry.notes)
        self.favorite_checkbox.setChecked(entry.is_favorite)
        
        # Load attached files
        if hasattr(entry, 'attached_files'):
            self.file_attachment_widget.set_attached_files(entry.attached_files)
    
    def get_entry(self) -> PasswordEntry:
        """Get entry from form data."""
        # Get file attachments
        attached_files = self.file_attachment_widget.get_files()
        return PasswordEntry(
            title=self.title_edit.text(),
            username=self.username_edit.text(),
            password=self.password_edit.text(),
            url=self.url_edit.text(),
            notes=self.notes_edit.toPlainText(),
            category=self.category_edit.text() or "General",
            is_favorite=self.favorite_checkbox.isChecked(),
            attached_files=attached_files
        ) 