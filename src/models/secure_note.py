"""
Secure Note Model
Represents a secure note.
"""

from datetime import datetime
from typing import Dict, List, Optional
from .file_entry import FileEntry


class SecureNote:
    """Represents a secure note."""
    
    def __init__(self, title: str, content: str, category: str = "General",
                 is_favorite: bool = False, attached_files: Optional[List[FileEntry]] = None):
        self.title = title
        self.content = content
        self.category = category
        self.is_favorite = is_favorite
        self.attached_files = attached_files or []
        self.created = datetime.now().isoformat()
        self.modified = self.created
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage."""
        return {
            'title': self.title,
            'content': self.content,
            'category': self.category,
            'is_favorite': self.is_favorite,
            'attached_files': [file_entry.to_dict() for file_entry in self.attached_files],
            'created': self.created,
            'modified': self.modified
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SecureNote':
        """Create from dictionary."""
        # Convert attached files from dict to FileEntry objects
        attached_files = []
        if 'attached_files' in data:
            for file_data in data['attached_files']:
                attached_files.append(FileEntry.from_dict(file_data))
        
        note = cls(data['title'], data['content'], data.get('category', 'General'),
                   data.get('is_favorite', False), attached_files)
        note.created = data.get('created', datetime.now().isoformat())
        note.modified = data.get('modified', note.created)
        return note 