"""
Card Entry Model
Represents a credit/debit card entry with metadata.
"""

from datetime import datetime
from typing import Dict, List, Optional
from .file_entry import FileEntry


class CardEntry:
    """Represents a credit/debit card entry with metadata."""
    
    def __init__(self, title: str, card_type: str, card_number: str, 
                 cardholder_name: str, expiry_month: str, expiry_year: str,
                 cvv: str = "", notes: str = "", category: str = "Cards",
                 is_favorite: bool = False, attached_files: Optional[List[FileEntry]] = None):
        self.title = title
        self.card_type = card_type  # Visa, Mastercard, Amex, etc.
        self.card_number = card_number
        self.cardholder_name = cardholder_name
        self.expiry_month = expiry_month
        self.expiry_year = expiry_year
        self.cvv = cvv
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
            'card_type': self.card_type,
            'card_number': self.card_number,
            'cardholder_name': self.cardholder_name,
            'expiry_month': self.expiry_month,
            'expiry_year': self.expiry_year,
            'cvv': self.cvv,
            'notes': self.notes,
            'category': self.category,
            'is_favorite': self.is_favorite,
            'attached_files': [file_entry.to_dict() for file_entry in self.attached_files],
            'created': self.created,
            'modified': self.modified
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'CardEntry':
        """Create from dictionary."""
        # Convert attached files from dict to FileEntry objects
        attached_files = []
        if 'attached_files' in data:
            for file_data in data['attached_files']:
                attached_files.append(FileEntry.from_dict(file_data))
        
        entry = cls(
            data['title'], data['card_type'], data['card_number'],
            data['cardholder_name'], data['expiry_month'], data['expiry_year'],
            data.get('cvv', ''), data.get('notes', ''), data.get('category', 'Cards'),
            data.get('is_favorite', False), attached_files
        )
        entry.created = data.get('created', datetime.now().isoformat())
        entry.modified = data.get('modified', entry.created)
        return entry 