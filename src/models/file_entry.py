"""
File Entry Model
Represents a file entry with metadata and encrypted file data.
"""

from datetime import datetime
from typing import Dict, Optional
import base64


class FileEntry:
    """Represents a file entry with metadata and encrypted file data."""
    
    def __init__(self, title: str, file_data: bytes, file_name: str, 
                 file_type: str = "", file_size: int = 0, category: str = "Files",
                 notes: str = "", is_favorite: bool = False):
        self.title = title
        self.file_data = file_data  # Raw file data (will be encrypted)
        self.file_name = file_name  # Original filename
        self.file_type = file_type  # File extension/type
        self.file_size = file_size  # File size in bytes
        self.category = category
        self.notes = notes
        self.is_favorite = is_favorite
        self.created = datetime.now().isoformat()
        self.modified = self.created
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage."""
        return {
            'title': self.title,
            'file_data': base64.b64encode(self.file_data).decode('utf-8'),  # Encode as base64
            'file_name': self.file_name,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'category': self.category,
            'notes': self.notes,
            'is_favorite': self.is_favorite,
            'created': self.created,
            'modified': self.modified
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'FileEntry':
        """Create from dictionary."""
        # Decode base64 file data back to bytes
        file_data = base64.b64decode(data['file_data'])
        
        entry = cls(
            data['title'],
            file_data,
            data['file_name'],
            data.get('file_type', ''),
            data.get('file_size', 0),
            data.get('category', 'Files'),
            data.get('notes', ''),
            data.get('is_favorite', False)
        )
        entry.created = data.get('created', datetime.now().isoformat())
        entry.modified = data.get('modified', entry.created)
        return entry
    
    def get_file_extension(self) -> str:
        """Get file extension from filename."""
        if '.' in self.file_name:
            return self.file_name.split('.')[-1].lower()
        return ""
    
    def get_file_size_formatted(self) -> str:
        """Get formatted file size string."""
        if self.file_size < 1024:
            return f"{self.file_size} B"
        elif self.file_size < 1024 * 1024:
            return f"{self.file_size / 1024:.1f} KB"
        elif self.file_size < 1024 * 1024 * 1024:
            return f"{self.file_size / (1024 * 1024):.1f} MB"
        else:
            return f"{self.file_size / (1024 * 1024 * 1024):.1f} GB"
    
    def is_image(self) -> bool:
        """Check if file is an image."""
        image_extensions = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp', 'svg'}
        return self.get_file_extension() in image_extensions
    
    def is_document(self) -> bool:
        """Check if file is a document."""
        document_extensions = {'pdf', 'doc', 'docx', 'txt', 'rtf', 'odt', 'pages'}
        return self.get_file_extension() in document_extensions
    
    def is_archive(self) -> bool:
        """Check if file is an archive."""
        archive_extensions = {'zip', 'rar', '7z', 'tar', 'gz', 'bz2'}
        return self.get_file_extension() in archive_extensions 