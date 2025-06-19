"""
File Attachment Widget
Reusable widget for attaching files to entries.
"""

import os
import tempfile
import shutil
import uuid
from typing import List, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QListWidget, QListWidgetItem, QFileDialog, QMessageBox,
    QMenu, QFrame
)
from PySide6.QtCore import Qt, Signal, QUrl, QTimer
from PySide6.QtGui import QIcon, QPixmap, QImage, QDesktopServices

from ..models import FileEntry


class FileAttachmentWidget(QWidget):
    """Widget for managing file attachments."""
    
    files_changed = Signal()  # Signal emitted when files are added/removed
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.attached_files: List[FileEntry] = []
        self.temp_files = {}  # Track temporary files: {file_entry_id: temp_path}
        self.setup_ui()
        
        # Timer to clean up temporary files
        self.cleanup_timer = QTimer()
        self.cleanup_timer.timeout.connect(self.cleanup_temp_files)
        self.cleanup_timer.start(300000)  # Clean up every 5 minutes
    
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Attached Files:"))
        
        self.add_file_btn = QPushButton("Add File")
        self.add_file_btn.clicked.connect(self.add_file)
        header_layout.addWidget(self.add_file_btn)
        
        layout.addLayout(header_layout)
        
        # File list
        self.file_list = QListWidget()
        self.file_list.setMaximumHeight(120)
        self.file_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self.show_context_menu)
        self.file_list.itemDoubleClicked.connect(self.open_file)  # Double-click to open
        layout.addWidget(self.file_list)
        
        # Info label
        self.info_label = QLabel("No files attached")
        self.info_label.setStyleSheet("color: #888; font-style: italic;")
        layout.addWidget(self.info_label)
    
    def add_file(self):
        """Add a new file attachment."""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Select Files to Attach", "",
            "All Files (*.*)"
        )
        
        for file_path in file_paths:
            try:
                # Read file data for storage (will be encrypted)
                with open(file_path, 'rb') as f:
                    file_data = f.read()
                
                original_name = os.path.basename(file_path)
                file_extension = os.path.splitext(original_name)[1]
                file_size = len(file_data)
                file_type = file_extension if file_extension else ""
                
                file_entry = FileEntry(
                    title=original_name,
                    file_data=file_data,
                    file_name=original_name,
                    file_type=file_type,
                    file_size=file_size,
                    category="Attachments"
                )
                
                self.attached_files.append(file_entry)
                self.add_file_to_list(file_entry)
                self.files_changed.emit()
                
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to attach file {os.path.basename(file_path)}: {str(e)}")
        
        self.update_info_label()
    
    def add_file_to_list(self, file_entry: FileEntry):
        """Add a file entry to the list widget."""
        item = QListWidgetItem()
        
        # Set icon based on file type
        if file_entry.is_image():
            item.setText("📷 " + file_entry.title)
        elif file_entry.is_document():
            item.setText("📄 " + file_entry.title)
        elif file_entry.is_archive():
            item.setText("📦 " + file_entry.title)
        else:
            item.setText("📁 " + file_entry.title)
        
        # Set tooltip with file info
        tooltip = f"Name: {file_entry.file_name}\n"
        tooltip += f"Size: {file_entry.get_file_size_formatted()}\n"
        tooltip += f"Type: {file_entry.file_type}\n"
        tooltip += "Double-click to open"
        item.setToolTip(tooltip)
        
        # Store the file entry in the item data
        item.setData(Qt.UserRole, file_entry)
        
        self.file_list.addItem(item)
    
    def open_file(self, item: QListWidgetItem):
        """Open a file using the system default application."""
        file_entry = item.data(Qt.UserRole)
        if not file_entry:
            return
        
        # Create temporary file for opening
        temp_path = self.create_temp_file(file_entry)
        if not temp_path:
            QMessageBox.critical(self, "Error", "Failed to create temporary file for opening.")
            return
        
        try:
            # Open file with system default application
            QDesktopServices.openUrl(QUrl.fromLocalFile(temp_path))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open file: {str(e)}")
            # Clean up temp file if opening failed
            self.remove_temp_file(file_entry)
    
    def create_temp_file(self, file_entry: FileEntry) -> Optional[str]:
        """Create a temporary file for opening."""
        try:
            # Create temporary file with proper extension
            temp_fd, temp_path = tempfile.mkstemp(suffix=file_entry.file_type)
            os.close(temp_fd)
            
            # Write file data to temporary file
            with open(temp_path, 'wb') as f:
                f.write(file_entry.file_data)
            
            # Store reference to temp file
            file_id = id(file_entry)
            self.temp_files[file_id] = temp_path
            
            return temp_path
        except Exception as e:
            print(f"Error creating temp file: {e}")
            return None
    
    def remove_temp_file(self, file_entry: FileEntry):
        """Remove temporary file for a file entry."""
        file_id = id(file_entry)
        if file_id in self.temp_files:
            temp_path = self.temp_files[file_id]
            try:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            except Exception as e:
                print(f"Error removing temp file {temp_path}: {e}")
            finally:
                del self.temp_files[file_id]
    
    def cleanup_temp_files(self):
        """Clean up all temporary files."""
        for file_id, temp_path in list(self.temp_files.items()):
            try:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            except Exception as e:
                print(f"Error cleaning up temp file {temp_path}: {e}")
            finally:
                del self.temp_files[file_id]
    
    def remove_file(self, index: int):
        """Remove a file attachment."""
        if 0 <= index < len(self.attached_files):
            removed_file = self.attached_files.pop(index)
            
            # Remove any associated temporary file
            self.remove_temp_file(removed_file)
            
            self.file_list.takeItem(index)
            self.files_changed.emit()
            self.update_info_label()
            return removed_file
        return None
    
    def show_context_menu(self, position):
        """Show context menu for file list."""
        item = self.file_list.itemAt(position)
        if item:
            menu = QMenu()
            
            open_action = menu.addAction("Open File")
            save_as_action = menu.addAction("Save As...")
            remove_action = menu.addAction("Remove File")
            
            action = menu.exec(self.file_list.mapToGlobal(position))
            
            if action == open_action:
                self.open_file(item)
            elif action == save_as_action:
                self.save_file_as(item)
            elif action == remove_action:
                self.remove_file_from_list(item)
    
    def save_file_as(self, item: QListWidgetItem):
        """Save a file to a new location."""
        file_entry = item.data(Qt.UserRole)
        if not file_entry:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save File As", file_entry.file_name,
            f"All Files (*.*);;{file_entry.file_type} Files (*{file_entry.file_type})"
        )
        
        if file_path:
            try:
                with open(file_path, 'wb') as f:
                    f.write(file_entry.file_data)
                QMessageBox.information(self, "Success", f"File saved to: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file: {str(e)}")
    
    def save_file(self, item: QListWidgetItem):
        """Legacy method - now calls save_file_as."""
        self.save_file_as(item)
    
    def remove_file_from_list(self, item: QListWidgetItem):
        """Remove a file from the list."""
        index = self.file_list.row(item)
        self.remove_file(index)
    
    def update_info_label(self):
        """Update the info label based on number of files."""
        count = len(self.attached_files)
        if count == 0:
            self.info_label.setText("No files attached")
        elif count == 1:
            self.info_label.setText("1 file attached (double-click to open)")
        else:
            self.info_label.setText(f"{count} files attached (double-click to open)")
    
    def get_files(self) -> List[FileEntry]:
        """Get the list of attached files."""
        return self.attached_files.copy()
    
    def get_attached_files(self) -> List[FileEntry]:
        """Get the list of attached files (legacy method)."""
        return self.get_files()
    
    def load_files(self, files: List[FileEntry]):
        """Load files from a list."""
        # Clean up any existing temp files
        self.cleanup_temp_files()
        
        self.attached_files = files.copy()
        self.file_list.clear()
        
        for file_entry in self.attached_files:
            self.add_file_to_list(file_entry)
        
        self.update_info_label()
        self.files_changed.emit()
    
    def set_attached_files(self, files: List[FileEntry]):
        """Set the list of attached files (legacy method)."""
        self.load_files(files)
    
    def clear_files(self):
        """Clear all attached files."""
        # Clean up all temporary files
        self.cleanup_temp_files()
        
        self.attached_files.clear()
        self.file_list.clear()
        self.update_info_label()
        self.files_changed.emit()
    
    def closeEvent(self, event):
        """Clean up temporary files when widget is closed."""
        self.cleanup_temp_files()
        super().closeEvent(event) 