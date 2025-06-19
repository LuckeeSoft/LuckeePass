"""
Password Generator Dialog
Dialog for generating passwords.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QSpinBox, QCheckBox, QMessageBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

from ..core import PasswordGenerator
from ..utils import apply_custom_title_bar


class PasswordGeneratorDialog(QDialog):
    """Dialog for generating passwords."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.generator = PasswordGenerator()
        self.generated_password = ""
        self.setup_ui()
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
        self.setWindowTitle("Password Generator")
        self.resize(350, 250)  # Reduced from 400x300 to 350x250
        
        layout = QVBoxLayout()
        
        # Length control
        length_layout = QHBoxLayout()
        length_layout.addWidget(QLabel("Length:"))
        self.length_spin = QSpinBox()
        self.length_spin.setRange(8, 128)
        self.length_spin.setValue(16)
        length_layout.addWidget(self.length_spin)
        length_layout.addStretch()
        layout.addLayout(length_layout)
        
        # Character options
        self.uppercase_cb = QCheckBox("Include Uppercase Letters")
        self.uppercase_cb.setChecked(True)
        layout.addWidget(self.uppercase_cb)
        
        self.digits_cb = QCheckBox("Include Numbers")
        self.digits_cb.setChecked(True)
        layout.addWidget(self.digits_cb)
        
        self.symbols_cb = QCheckBox("Include Symbols")
        self.symbols_cb.setChecked(True)
        layout.addWidget(self.symbols_cb)
        
        self.exclude_similar_cb = QCheckBox("Exclude Similar Characters (l, 1, I, O, 0, S, 5)")
        self.exclude_similar_cb.setChecked(True)
        layout.addWidget(self.exclude_similar_cb)
        
        # Generated password display
        layout.addWidget(QLabel("Generated Password:"))
        self.password_display = QLineEdit()
        self.password_display.setReadOnly(True)
        self.password_display.setFont(QFont("Courier", 12))
        layout.addWidget(self.password_display)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.generate_btn = QPushButton("Generate")
        self.generate_btn.clicked.connect(self.generate_password)
        button_layout.addWidget(self.generate_btn)
        
        self.copy_btn = QPushButton("Copy to Clipboard")
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        button_layout.addWidget(self.copy_btn)
        
        self.accept_btn = QPushButton("Use This Password")
        self.accept_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.accept_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Generate initial password
        self.generate_password()
    
    def generate_password(self):
        """Generate a new password."""
        try:
            self.generated_password = self.generator.generate_password(
                length=self.length_spin.value(),
                use_uppercase=self.uppercase_cb.isChecked(),
                use_digits=self.digits_cb.isChecked(),
                use_symbols=self.symbols_cb.isChecked(),
                exclude_similar=self.exclude_similar_cb.isChecked()
            )
            self.password_display.setText(self.generated_password)
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
    
    def copy_to_clipboard(self):
        """Copy password to clipboard."""
        from PySide6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(self.generated_password)
        QMessageBox.information(self, "Copied", "Password copied to clipboard!") 