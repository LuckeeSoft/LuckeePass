"""
Welcome Back Dialog
Dialog for returning users to upload their existing data and confirm their master password.
"""

import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QMessageBox, QFrame, QApplication, QFileDialog,
    QProgressBar, QTextEdit
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QPixmap

from ..core import UserManager, PasswordManager
from ..utils import apply_custom_title_bar
from src.utils.resource_path import resource_path, get_appdata_path

class WelcomeBackDialog(QDialog):
    """Dialog for returning users to upload their existing data and confirm their master password."""
    
    def __init__(self, user_manager: UserManager, parent=None):
        super().__init__(parent)
        self.user_manager = user_manager
        self.master_password = ""
        self.uploaded_file_path = ""
        self.password_manager = None
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
        self.setWindowTitle("Welcome Back to LuckeePass")
        self.setModal(True)
        self.resize(400, 400)
        
        layout = QVBoxLayout()
        layout.setSpacing(5) # Reduced overall layout spacing
        
        # Logo
        self.logo_label = QLabel()
        pixmap = QPixmap(resource_path("images/luckeepasslogo.png"))
        if not pixmap.isNull():
            self.logo_label.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.logo_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(self.logo_label)
        else:
            print("Failed to load luckeepasslogo.png")

        # Welcome header
        welcome_label = QLabel("Welcome Back to LuckeePass!")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setFont(QFont("Jua", 18, QFont.Bold))
        welcome_label.setStyleSheet("color: #60A3D9; margin: 5px;") # Reduced margin
        layout.addWidget(welcome_label)
        
        # Welcome message
        message_label = QLabel(
            "Upload your existing LuckeePass data file (.lp) and confirm your master password to restore your vault."
        )
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("margin: 0px; padding: 5px; background-color: #243447; border-radius: 5px;") # Reduced margin
        layout.addWidget(message_label)
        
        # File Upload Section
        file_frame = QFrame()
        file_frame.setFrameStyle(QFrame.NoFrame)
        file_frame.setStyleSheet("QFrame { border: none; border-radius: 5px; padding: 5px; }")
        file_layout = QHBoxLayout(file_frame)
        file_layout.setContentsMargins(0, 0, 0, 0)
        file_layout.setSpacing(5)
        
        # File path display
        self.file_path_label = QLabel("No file selected")
        self.file_path_label.setStyleSheet("padding: 4px; background-color: #1E2B38; border: 1px solid #3A4C60; border-radius: 3px; color: #dce6f2;")
        self.file_path_label.setWordWrap(True)
        file_layout.addWidget(self.file_path_label, 1) # Make it expanding
        
        # Upload button
        self.upload_btn = QPushButton("Browse")
        self.upload_btn.clicked.connect(self.browse_file)
        self.upload_btn.setAutoDefault(False) # Prevent it from being the default button
        self.upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #2c3e50; color: #dce6f2; border: 1px solid #1a2636;
                padding: 5px 10px; border-radius: 4px;
            }
            QPushButton:hover { background-color: #1a2636; }
        """)
        file_layout.addWidget(self.upload_btn) # Add it directly to file_layout
        
        layout.addWidget(file_frame)
        
        # Master Password Section
        password_frame = QFrame()
        password_frame.setFrameStyle(QFrame.NoFrame)
        password_frame.setStyleSheet("QFrame { border: none; border-radius: 5px; padding: 5px; }")
        password_layout = QVBoxLayout(password_frame)
        password_layout.setContentsMargins(0, 0, 0, 0)
        password_layout.setSpacing(2)
        
        self.master_password_label = QLabel("Master Password:")
        self.master_password_label.setStyleSheet("margin-bottom: 2px;")
        password_layout.addWidget(self.master_password_label)
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("Enter the master password for your data file")
        self.password_edit.setStyleSheet("margin-bottom: 5px;")
        password_layout.addWidget(self.password_edit)
        
        layout.addWidget(password_frame)
        
        # Status and Progress
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #dce6f2; padding: 3px;")
        layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setAutoDefault(False) # Prevent it from being the default button
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d; color: white; border: none;
                padding: 8px 16px; border-radius: 4px; font-weight: bold;
            }
            QPushButton:hover { background-color: #5a6268; }
        """)
        button_layout.addWidget(self.cancel_btn)
        
        button_layout.addStretch()
        
        self.restore_btn = QPushButton("Restore Data")
        self.restore_btn.clicked.connect(self.handle_restore)
        self.restore_btn.setEnabled(False) # It will be enabled/disabled by update_restore_button_state
        self.restore_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078D7; color: white; border: none;
                padding: 8px 16px; border-radius: 4px; font-weight: bold;
            }
            QPushButton:hover { background-color: #005B9C; }
            QPushButton:disabled { background-color: #6c757d; }
        """)
        button_layout.addWidget(self.restore_btn)

        layout.addLayout(button_layout)
        layout.addStretch(1)

        self.setLayout(layout)
        
        # Connect enter key
        self.password_edit.returnPressed.connect(self.handle_restore)
        
        # Connect password field changes to update button state
        self.password_edit.textChanged.connect(self.update_restore_button_state)
    
    def browse_file(self):
        """Open file dialog to select .lp file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select LuckeePass Data File",
            "",
            "LuckeePass Files (*.lp);;All Files (*)"
        )
        
        if file_path:
            self.uploaded_file_path = file_path
            self.file_path_label.setText(f"Selected: {os.path.basename(file_path)}")
            self.file_path_label.setStyleSheet("padding: 4px; background-color: #1E2B38; border: 1px solid #3A4C60; border-radius: 3px; color: #28a745;")
            self.update_restore_button_state()
    
    def update_restore_button_state(self):
        """Update the restore button state based on file selection and password entry."""
        has_file = bool(self.uploaded_file_path)
        has_password = bool(self.password_edit.text().strip())
        
        self.restore_btn.setEnabled(has_file and has_password)
        
        # Use QPushButton.setDefault() directly
        if has_file and has_password:
            self.restore_btn.setDefault(True)
        else:
            self.restore_btn.setDefault(False)

        self.cancel_btn.setAutoDefault(False) # Ensure cancel is not default
        self.upload_btn.setAutoDefault(False) # Ensure browse is not default
    
    def handle_restore(self):
        """Handle the data restoration process."""
        if not self.uploaded_file_path:
            QMessageBox.warning(self, "No File Selected", "Please select a .lp file to restore.")
            return
        
        if not self.password_edit.text().strip():
            QMessageBox.warning(self, "No Password", "Please enter your master password.")
            return
        
        master_password = self.password_edit.text().strip()
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.status_label.setText("Verifying file and testing password...")
        self.restore_btn.setEnabled(False)
        self.cancel_btn.setEnabled(False)
        
        # Process in a timer to allow UI updates
        QTimer.singleShot(100, lambda: self.verify_and_restore(master_password))
    
    def verify_and_restore(self, master_password):
        """Verify the file and password, then restore data."""
        try:
            # First, verify the file is a valid .lp file
            if not PasswordManager.is_valid_lp_file(self.uploaded_file_path):
                raise ValueError("The selected file is not a valid LuckeePass data file.")
            
            # Get backup info to show user what they're restoring
            backup_info = PasswordManager.get_backup_info(self.uploaded_file_path)
            
            # Create a temporary password manager to test the password
            temp_user_manager = UserManager()
            temp_password_manager = PasswordManager(master_password, temp_user_manager)
            
            # Try to load the data with the provided password
            with open(self.uploaded_file_path, 'rb') as f:
                lp_data = f.read()
            
            # Test if we can decrypt the data
            temp_password_manager.import_data(lp_data)
            
            # If we get here, the password is correct
            self.status_label.setText("Password verified successfully!")
            self.progress_bar.setVisible(False)
            
            # Set the master password and create the real password manager
            self.user_manager.set_master_password(master_password)
            self.password_manager = PasswordManager(master_password, self.user_manager)
            self.password_manager.data_file = get_appdata_path("luckeepass_data.lp")
            
            # Import the data
            self.password_manager.import_data(lp_data)
            
            # Save the data to the local file
            self.password_manager.save_data()
            
            self.master_password = master_password
            
            # Count the actual restored items
            password_count = len(self.password_manager.passwords)
            note_count = len(self.password_manager.notes)
            card_count = len(self.password_manager.cards)
            identity_count = len(self.password_manager.identities)
            file_count = len(self.password_manager.files)
            
            QMessageBox.information(
                self,
                "Restoration Complete!",
                f"Successfully restored {password_count} logins, "
                f"{note_count} notes, "
                f"{card_count} cards, "
                f"{identity_count} identities.\n\nYour vault is now ready to use!"
            )
            
            self.accept()
            
        except Exception as e:
            self.progress_bar.setVisible(False)
            self.status_label.setText("")
            self.restore_btn.setEnabled(True)
            self.cancel_btn.setEnabled(True)
            
            if "Invalid .lp file format" in str(e):
                QMessageBox.critical(
                    self,
                    "Invalid File",
                    "The selected file is not a valid LuckeePass data file.\n\nPlease select a .lp file created by LuckeePass."
                )
            elif "Failed to decrypt" in str(e) or "Invalid master password" in str(e):
                QMessageBox.critical(
                    self,
                    "Invalid Password",
                    "The master password you entered is incorrect for this data file.\n\nPlease verify your master password and try again."
                )
                self.password_edit.clear()
                self.password_edit.setFocus()
            else:
                QMessageBox.critical(
                    self,
                    "Restoration Failed",
                    f"Failed to restore data: {str(e)}\n\nPlease ensure the file is not corrupted and try again."
                )
    
    def reset_ui(self):
        """Reset the UI to initial state."""
        self.progress_bar.setVisible(False)
        self.status_label.setText("")
        self.restore_btn.setEnabled(True)
        self.cancel_btn.setEnabled(True)
        self.update_restore_button_state() 