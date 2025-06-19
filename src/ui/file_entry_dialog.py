"""
File Entry Dialog
Dialog for adding and editing file entries.
"""

import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTextEdit, QComboBox, QCheckBox, QFileDialog,
    QMessageBox, QGroupBox, QFormLayout, QScrollArea
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap, QImage
import io

from ..models import FileEntry


class FileEntryDialog(QDialog):
    """Dialog for adding and editing file entries."""
    
    def __init__(self, file_entry: FileEntry = None, parent=None):
        super().__init__(parent)
        self.file_entry = file_entry
        self.selected_file_path = ""
        self.selected_file_data = b""
        
        self.setWindowTitle("Add File" if file_entry is None else "Edit File")
        self.setModal(True)
        self.setFixedSize(600, 500)  # Increased size for thumbnail
        
        self.setup_ui()
        
        if file_entry:
            self.load_file_data()
    
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Title:")
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Enter a title for this file")
        layout.addWidget(title_label)
        layout.addWidget(self.title_edit)
        
        # File selection and preview
        file_group = QGroupBox("File")
        file_layout = QHBoxLayout(file_group)  # Changed to horizontal layout
        
        # Left side - file selection
        file_selection_layout = QVBoxLayout()
        
        file_info_layout = QHBoxLayout()
        self.file_path_label = QLabel("No file selected")
        self.file_path_label.setStyleSheet("color: #7F8C8D; font-style: italic;")
        file_info_layout.addWidget(self.file_path_label)
        
        self.select_file_btn = QPushButton("Select File")
        self.select_file_btn.clicked.connect(self.select_file)
        file_info_layout.addWidget(self.select_file_btn)
        
        file_selection_layout.addLayout(file_info_layout)
        
        # File details
        self.file_details_label = QLabel("")
        self.file_details_label.setStyleSheet("color: #95A5A6; font-size: 10px;")
        file_selection_layout.addWidget(self.file_details_label)
        
        file_layout.addLayout(file_selection_layout)
        
        # Right side - thumbnail preview
        preview_layout = QVBoxLayout()
        preview_label = QLabel("Preview:")
        preview_label.setStyleSheet("font-weight: bold;")
        preview_layout.addWidget(preview_label)
        
        self.preview_label = QLabel()
        self.preview_label.setFixedSize(150, 150)
        self.preview_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #BDC3C7;
                border-radius: 5px;
                background-color: #F8F9FA;
            }
        """)
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setText("No preview\navailable")
        self.preview_label.setWordWrap(True)
        
        preview_layout.addWidget(self.preview_label)
        file_layout.addLayout(preview_layout)
        
        layout.addWidget(file_group)
        
        # Category
        category_label = QLabel("Category:")
        self.category_edit = QComboBox()
        self.category_edit.setEditable(True)
        self.category_edit.addItems(["Files", "Documents", "Images", "Archives", "Personal", "Work"])
        self.category_edit.setCurrentText("Files")
        layout.addWidget(category_label)
        layout.addWidget(self.category_edit)
        
        # Notes
        notes_label = QLabel("Notes:")
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(100)
        self.notes_edit.setPlaceholderText("Add any notes about this file...")
        layout.addWidget(notes_label)
        layout.addWidget(self.notes_edit)
        
        # Favorite checkbox (place below the file attachment box and above the Save/Cancel buttons)
        self.favorite_checkbox = QCheckBox("Mark as favorite")
        layout.addWidget(self.favorite_checkbox)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.handle_save)
        self.save_btn.setDefault(True)
        button_layout.addWidget(self.save_btn)
        
        layout.addLayout(button_layout)
    
    def select_file(self):
        """Open file dialog to select a file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File", "", 
            "All Files (*.*);;Images (*.png *.jpg *.jpeg *.gif *.bmp *.tiff *.webp *.svg);;"
            "Documents (*.pdf *.doc *.docx *.txt *.rtf *.odt *.pages);;"
            "Archives (*.zip *.rar *.7z *.tar *.gz *.bz2)"
        )
        
        if file_path:
            try:
                with open(file_path, 'rb') as f:
                    self.selected_file_data = f.read()
                
                self.selected_file_path = file_path
                file_name = os.path.basename(file_path)
                file_size = len(self.selected_file_data)
                
                # Update UI
                self.file_path_label.setText(file_name)
                self.file_path_label.setStyleSheet("color: #2ECC71; font-weight: bold;")
                
                # Show file details
                size_str = self.format_file_size(file_size)
                file_ext = os.path.splitext(file_name)[1].lower()
                self.file_details_label.setText(f"Size: {size_str} | Type: {file_ext or 'Unknown'}")
                
                # Generate thumbnail preview
                self.generate_thumbnail(file_name, file_ext)
                
                # Auto-set title if empty
                if not self.title_edit.text():
                    self.title_edit.setText(os.path.splitext(file_name)[0])
                
                # Auto-set category based on file type
                if file_ext in {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg'}:
                    self.category_edit.setCurrentText("Images")
                elif file_ext in {'.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.pages'}:
                    self.category_edit.setCurrentText("Documents")
                elif file_ext in {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'}:
                    self.category_edit.setCurrentText("Archives")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not read file: {str(e)}")
    
    def generate_thumbnail(self, file_name: str, file_ext: str):
        """Generate thumbnail preview for supported file types."""
        try:
            if file_ext in {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}:
                # Image thumbnail
                image = QImage()
                if image.loadFromData(self.selected_file_data):
                    pixmap = QPixmap.fromImage(image)
                    scaled_pixmap = pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.preview_label.setPixmap(scaled_pixmap)
                    self.preview_label.setStyleSheet("border: 2px solid #2ECC71; border-radius: 5px;")
                else:
                    self.preview_label.setText("Invalid\nimage file")
                    self.preview_label.setStyleSheet("border: 2px dashed #E74C3C; border-radius: 5px; background-color: #F8F9FA;")
            
            elif file_ext == '.svg':
                # SVG thumbnail
                pixmap = QPixmap()
                if pixmap.loadFromData(self.selected_file_data):
                    scaled_pixmap = pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.preview_label.setPixmap(scaled_pixmap)
                    self.preview_label.setStyleSheet("border: 2px solid #2ECC71; border-radius: 5px;")
                else:
                    self.preview_label.setText("Invalid\nSVG file")
                    self.preview_label.setStyleSheet("border: 2px dashed #E74C3C; border-radius: 5px; background-color: #F8F9FA;")
            
            elif file_ext in {'.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.pages'}:
                # Document icon
                self.preview_label.setText("📄\nDocument")
                self.preview_label.setStyleSheet("border: 2px solid #3498DB; border-radius: 5px; background-color: #EBF3FD; font-size: 24px;")
            
            elif file_ext in {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'}:
                # Archive icon
                self.preview_label.setText("📦\nArchive")
                self.preview_label.setStyleSheet("border: 2px solid #F39C12; border-radius: 5px; background-color: #FEF9E7; font-size: 24px;")
            
            else:
                # Generic file icon
                self.preview_label.setText("📁\nFile")
                self.preview_label.setStyleSheet("border: 2px solid #95A5A6; border-radius: 5px; background-color: #F8F9FA; font-size: 24px;")
                
        except Exception as e:
            self.preview_label.setText("Preview\nerror")
            self.preview_label.setStyleSheet("border: 2px dashed #E74C3C; border-radius: 5px; background-color: #F8F9FA;")
    
    def format_file_size(self, size_bytes):
        """Format file size in human readable format."""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
    
    def load_file_data(self):
        """Load existing file data into the form."""
        if self.file_entry:
            self.title_edit.setText(self.file_entry.title)
            self.category_edit.setCurrentText(self.file_entry.category)
            self.notes_edit.setPlainText(self.file_entry.notes)
            self.favorite_checkbox.setChecked(self.file_entry.is_favorite)
            
            # Show existing file info
            self.file_path_label.setText(self.file_entry.file_name)
            self.file_path_label.setStyleSheet("color: #2ECC71; font-weight: bold;")
            
            size_str = self.file_entry.get_file_size_formatted()
            file_ext = self.file_entry.get_file_extension()
            self.file_details_label.setText(f"Size: {size_str} | Type: {file_ext or 'Unknown'}")
            
            # Store existing file data
            self.selected_file_data = self.file_entry.file_data
            self.selected_file_path = self.file_entry.file_name
            
            # Generate thumbnail for existing file
            self.generate_thumbnail(self.file_entry.file_name, file_ext)
    
    def handle_save(self):
        """Handle save button click."""
        title = self.title_edit.text().strip()
        category = self.category_edit.currentText().strip()
        notes = self.notes_edit.toPlainText().strip()
        is_favorite = self.favorite_checkbox.isChecked()
        
        # Validation
        if not title:
            QMessageBox.warning(self, "Validation Error", "Please enter a title.")
            return
        
        if not self.selected_file_data and not self.file_entry:
            QMessageBox.warning(self, "Validation Error", "Please select a file.")
            return
        
        # Create or update file entry
        if self.file_entry:
            # Update existing entry
            self.file_entry.title = title
            self.file_entry.category = category
            self.file_entry.notes = notes
            self.file_entry.is_favorite = is_favorite
            
            # Update file data if new file was selected
            if self.selected_file_data:
                self.file_entry.file_data = self.selected_file_data
                self.file_entry.file_name = os.path.basename(self.selected_file_path)
                self.file_entry.file_type = os.path.splitext(self.file_entry.file_name)[1]
                self.file_entry.file_size = len(self.selected_file_data)
        else:
            # Create new entry
            file_name = os.path.basename(self.selected_file_path) if self.selected_file_path else "Unknown"
            file_type = os.path.splitext(file_name)[1]
            file_size = len(self.selected_file_data)
            
            self.file_entry = FileEntry(
                title=title,
                file_data=self.selected_file_data,
                file_name=file_name,
                file_type=file_type,
                file_size=file_size,
                category=category,
                notes=notes,
                is_favorite=is_favorite
            )
        
        self.accept()
    
    def get_entry(self) -> FileEntry:
        """Get the file entry."""
        return self.file_entry 