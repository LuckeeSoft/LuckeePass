"""
Identity Entry Model
Represents an identity entry with personal information.
"""

from datetime import datetime
from typing import Dict, List, Optional
from .file_entry import FileEntry


class IdentityEntry:
    """Represents an identity entry with personal information."""
    
    def __init__(self, title: str, first_name: str, last_name: str, 
                 email: str = "", phone: str = "", address: str = "",
                 city: str = "", state: str = "", zip_code: str = "",
                 country: str = "", date_of_birth: str = "", 
                 social_security_number: str = "", driver_license: str = "",
                 passport_number: str = "", notes: str = "", category: str = "Identity",
                 is_favorite: bool = False, attached_files: Optional[List[FileEntry]] = None):
        self.title = title
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.address = address
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.country = country
        self.date_of_birth = date_of_birth
        self.social_security_number = social_security_number
        self.driver_license = driver_license
        self.passport_number = passport_number
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
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'country': self.country,
            'date_of_birth': self.date_of_birth,
            'social_security_number': self.social_security_number,
            'driver_license': self.driver_license,
            'passport_number': self.passport_number,
            'notes': self.notes,
            'category': self.category,
            'is_favorite': self.is_favorite,
            'attached_files': [file_entry.to_dict() for file_entry in self.attached_files],
            'created': self.created,
            'modified': self.modified
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'IdentityEntry':
        """Create from dictionary."""
        # Convert attached files from dict to FileEntry objects
        attached_files = []
        if 'attached_files' in data:
            for file_data in data['attached_files']:
                attached_files.append(FileEntry.from_dict(file_data))
        
        entry = cls(
            data['title'], data['first_name'], data['last_name'],
            data.get('email', ''), data.get('phone', ''), data.get('address', ''),
            data.get('city', ''), data.get('state', ''), data.get('zip_code', ''),
            data.get('country', ''), data.get('date_of_birth', ''),
            data.get('social_security_number', ''), data.get('driver_license', ''),
            data.get('passport_number', ''), data.get('notes', ''), data.get('category', 'Identity'),
            data.get('is_favorite', False), attached_files
        )
        entry.created = data.get('created', datetime.now().isoformat())
        entry.modified = data.get('modified', entry.created)
        return entry 