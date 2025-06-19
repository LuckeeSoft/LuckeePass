"""
Secure Note Dialog
Dialog for creating/editing secure notes.
"""

from typing import Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, 
    QTextEdit, QComboBox, QDialogButtonBox, QCheckBox, QFormLayout, QHBoxLayout, QPushButton, QScrollArea, QWidget, QSizePolicy, QMessageBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

from ..models import SecureNote
from .file_attachment_widget import FileAttachmentWidget
from ..utils import apply_custom_title_bar


class SecureNoteDialog(QDialog):
    """Dialog for creating/editing secure notes."""
    
    def __init__(self, note: Optional[SecureNote] = None, parent=None):
        super().__init__(parent)
        self.note = note
        self.setup_ui()
        if note:
            self.load_note(note)
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
        """Setup the dialog UI."""
        self.setWindowTitle("Secure Note")
        self.setModal(True)
        self.resize(500, 540)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(12, 12, 12, 12)

        # Form layout for fields
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form_layout.setFormAlignment(Qt.AlignTop)
        form_layout.setHorizontalSpacing(16)
        form_layout.setVerticalSpacing(10)

        # --- Note Information Section Heading (as a row in the form layout) ---
        note_info_label = QLabel("Note Information")
        note_info_label.setFont(QFont("Arial", 12, QFont.Bold))
        note_info_label.setStyleSheet("color: #0078D7; margin-top: 10px;")
        form_layout.addRow(note_info_label)

        # Title
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Enter a title for this note")
        form_layout.addRow("Title:", self.title_edit)

        # Category
        self.category_edit = QComboBox()
        self.category_edit.setEditable(True)
        self.category_edit.addItems(["General", "Personal", "Work", "Finance", "Other"])
        form_layout.addRow("Category:", self.category_edit)

        # Content
        self.content_edit = QTextEdit()
        self.content_edit.setMinimumHeight(90)
        self.content_edit.setMaximumHeight(120)
        self.content_edit.setPlaceholderText("Write your secure note here...")
        form_layout.addRow("Content:", self.content_edit)

        main_layout.addLayout(form_layout)

        # --- File Attachments Section Heading and Widget (outside form layout) ---
        file_label = QLabel("File Attachments")
        file_label.setFont(QFont("Arial", 12, QFont.Bold))
        file_label.setStyleSheet("color: #0078D7; margin-top: 10px;")
        main_layout.addWidget(file_label)
        self.file_attachment_widget = FileAttachmentWidget()
        main_layout.addWidget(self.file_attachment_widget)

        # Favorite Checkbox (moved below file attachments)
        self.favorite_checkbox = QCheckBox("Favorite")
        main_layout.addWidget(self.favorite_checkbox)

        # Buttons (full width, matching Identity dialog)
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.save_btn.setDefault(True)
        self.save_btn.setMinimumHeight(36)
        self.save_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078D7; color: white; border: none;
                padding: 10px 20px; border-radius: 4px; font-weight: bold;
            }
            QPushButton:hover { background-color: #005B9C; }
        """)
        self.save_btn.clicked.connect(self.handle_save)
        button_layout.addWidget(self.save_btn)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setMinimumHeight(36)
        self.cancel_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #6C757D; color: white; border: none;
                padding: 10px 20px; border-radius: 4px; font-weight: bold;
            }
            QPushButton:hover { background-color: #545B62; }
        """)
        button_layout.addWidget(self.cancel_btn)
        main_layout.addLayout(button_layout)
    
    def load_note(self, note: SecureNote):
        """Load note data into dialog."""
        self.title_edit.setText(note.title)
        self.category_edit.setCurrentText(note.category)
        self.content_edit.setPlainText(note.content)
        self.favorite_checkbox.setChecked(note.is_favorite)
        
        # Load attached files
        if hasattr(note, 'attached_files'):
            self.file_attachment_widget.set_attached_files(note.attached_files)
    
    def get_note(self) -> SecureNote:
        """Get note data from dialog."""
        # Get file attachments
        attached_files = self.file_attachment_widget.get_files()
        return SecureNote(
            self.title_edit.text(),
            self.content_edit.toPlainText(),
            self.category_edit.currentText(),
            self.favorite_checkbox.isChecked(),
            attached_files
        )

    def handle_save(self):
        """Validate and accept the dialog if valid."""
        title = self.title_edit.text().strip()
        content = self.content_edit.toPlainText().strip()
        if not title:
            QMessageBox.warning(self, "Missing Information", "Please enter a title for the note.")
            return
        if not content:
            QMessageBox.warning(self, "Missing Information", "Please enter some content for the note.")
            return
        self.accept() 