"""
Password Entry Model
Represents a password entry with metadata.
"""

from datetime import datetime
from typing import Dict, List, Optional
from .file_entry import FileEntry


class PasswordEntry:
    """Represents a password entry with metadata."""
    
    def __init__(self, title: str, username: str, password: str, 
                 url: str = "", notes: str = "", category: str = "General",
                 is_favorite: bool = False, attached_files: Optional[List[FileEntry]] = None):
        self.title = title
        self.username = username
        self.password = password
        self.url = url
        self.notes = notes
        self.category = category
        self.is_favorite = is_favorite
        self.attached_files = attached_files or []
        self.created = datetime.now().isoformat()
        self.modified = self.created
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage."""
        return {
            'title': self.title,
            'username': self.username,
            'password': self.password,
            'url': self.url,
            'notes': self.notes,
            'category': self.category,
            'is_favorite': self.is_favorite,
            'attached_files': [file_entry.to_dict() for file_entry in self.attached_files],
            'created': self.created,
            'modified': self.modified
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PasswordEntry':
        """Create from dictionary."""
        # Convert attached files from dict to FileEntry objects
        attached_files = []
        if 'attached_files' in data:
            for file_data in data['attached_files']:
                attached_files.append(FileEntry.from_dict(file_data))
        
        entry = cls(
            data['title'], data['username'], data['password'],
            data.get('url', ''), data.get('notes', ''), data.get('category', 'General'),
            data.get('is_favorite', False), attached_files
        )
        entry.created = data.get('created', datetime.now().isoformat())
        entry.modified = data.get('modified', entry.created)
        return entry 