"""
Password Manager
Main password manager class handling data storage and operations.
"""

import os
import json
import base64
import secrets
import string
from datetime import datetime
from typing import List, Dict, Optional
import hashlib # Import hashlib for deterministic salt generation

import bcrypt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from ..models import PasswordEntry, SecureNote, CardEntry, IdentityEntry, FileEntry
from .encryption_manager import EncryptionManager
from .user_manager import UserManager
from src.utils.resource_path import get_appdata_path


class PasswordManager:
    """Main password manager class handling data storage and operations."""
    
    def __init__(self, master_password: str, user_manager: UserManager):
        self.master_password = master_password
        self.user_manager = user_manager
        self.data_file = get_appdata_path("luckeepass_data.lp")
        self.passwords: List[PasswordEntry] = []
        self.notes: List[SecureNote] = []
        self.cards: List[CardEntry] = []
        self.identities: List[IdentityEntry] = []
        self.files: List[FileEntry] = []
        self.categories = set()
        
        # Initialize encryption_manager using the vault salt from user_manager
        vault_salt = self.user_manager.get_vault_salt()
        if vault_salt is not None:
            self.encryption_manager = EncryptionManager(master_password, salt=vault_salt)
        else:
            # Fallback for new installations
            self.encryption_manager = EncryptionManager(master_password)
    
    def save_data(self) -> None:
        """Save all data to local file."""
        try:
            lp_data = self.export_data()
            with open(self.data_file, 'wb') as f:
                f.write(lp_data)
        except Exception as e:
            raise Exception(f"Failed to save data: {str(e)}")
    
    def load_data(self) -> None:
        """Load data from local file."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'rb') as f:
                    lp_data = f.read()
                
                # Check if file is empty
                if len(lp_data) == 0:
                    return
                
                # Try to load the data
                try:
                    self.import_data(lp_data)
                except Exception as e:
                    print("This usually means the master password is different from when the data was created.")
                    print("Starting with fresh data. You can delete the data file to avoid this message.")
                    # Clear any partially loaded data
                    self.passwords = []
                    self.notes = []
                    self.cards = []
                    self.identities = []
                    self.categories = set()
                    
            except Exception as e:
                # If loading fails, start with empty data
                print("Starting with fresh data")
                self.passwords = []
                self.notes = []
                self.cards = []
                self.identities = []
                self.categories = set()
        else:
            print("No existing data file found, starting fresh")
    
    def add_password(self, entry: PasswordEntry) -> None:
        """Add a password entry."""
        entry.modified = datetime.now().isoformat()
        self.passwords.append(entry)
        self.categories.add(entry.category)
    
    def update_password(self, index: int, entry: PasswordEntry) -> None:
        """Update a password entry."""
        entry.modified = datetime.now().isoformat()
        self.passwords[index] = entry
        self.categories.add(entry.category)
    
    def delete_password(self, index: int) -> None:
        """Delete a password entry."""
        del self.passwords[index]
    
    def add_note(self, note: SecureNote) -> None:
        """Add a secure note."""
        note.modified = datetime.now().isoformat()
        self.notes.append(note)
        self.categories.add(note.category)
    
    def update_note(self, index: int, note: SecureNote) -> None:
        """Update a secure note."""
        note.modified = datetime.now().isoformat()
        self.notes[index] = note
        self.categories.add(note.category)
    
    def delete_note(self, index: int) -> None:
        """Delete a secure note."""
        del self.notes[index]
    
    def add_card(self, card: CardEntry) -> None:
        """Add a card entry."""
        card.modified = datetime.now().isoformat()
        self.cards.append(card)
        self.categories.add(card.category)
    
    def update_card(self, index: int, card: CardEntry) -> None:
        """Update a card entry."""
        card.modified = datetime.now().isoformat()
        self.cards[index] = card
        self.categories.add(card.category)
    
    def delete_card(self, index: int) -> None:
        """Delete a card entry."""
        del self.cards[index]
    
    def add_identity(self, identity: IdentityEntry) -> None:
        """Add an identity entry."""
        identity.modified = datetime.now().isoformat()
        self.identities.append(identity)
        self.categories.add(identity.category)
    
    def update_identity(self, index: int, identity: IdentityEntry) -> None:
        """Update an identity entry."""
        identity.modified = datetime.now().isoformat()
        self.identities[index] = identity
        self.categories.add(identity.category)
    
    def delete_identity(self, index: int) -> None:
        """Delete an identity entry."""
        del self.identities[index]
    
    def add_file(self, file_entry: FileEntry) -> None:
        """Add a file entry."""
        file_entry.modified = datetime.now().isoformat()
        self.files.append(file_entry)
        self.categories.add(file_entry.category)
    
    def update_file(self, index: int, file_entry: FileEntry) -> None:
        """Update a file entry."""
        file_entry.modified = datetime.now().isoformat()
        self.files[index] = file_entry
        self.categories.add(file_entry.category)
    
    def delete_file(self, index: int) -> None:
        """Delete a file entry."""
        del self.files[index]
    
    def export_data(self) -> bytes:
        """Export all data as encrypted .lp file format."""
        data = {
            'passwords': [entry.to_dict() for entry in self.passwords],
            'notes': [note.to_dict() for note in self.notes],
            'cards': [card.to_dict() for card in self.cards],
            'identities': [identity.to_dict() for identity in self.identities],
            'files': [file.to_dict() for file in self.files],
            'version': '1.0',
            'app_name': 'LuckeePass',
            'company': 'LuckeeSoft',
            'created': datetime.now().isoformat()
        }
        
        # Add salt to the data for encryption
        data['encryption_salt'] = base64.b64encode(self.encryption_manager.get_salt()).decode('utf-8')

        # Encrypt each sensitive field
        encrypted_data = {
            'passwords': [],
            'notes': [],
            'cards': [],
            'identities': [],
            'files': [],
            'version': '1.0',
            'app_name': 'LuckeePass',
            'company': 'LuckeeSoft',
            'created': data['created'],
            'encryption_salt': data['encryption_salt']  # Include salt in encrypted data
        }
        
        for entry in data['passwords']:
            encrypted_entry = entry.copy()
            encrypted_entry['password'] = self.encryption_manager.encrypt(entry['password'])
            encrypted_entry['notes'] = self.encryption_manager.encrypt(entry['notes'])
            encrypted_data['passwords'].append(encrypted_entry)
        
        for note in data['notes']:
            encrypted_note = note.copy()
            encrypted_note['content'] = self.encryption_manager.encrypt(note['content'])
            encrypted_data['notes'].append(encrypted_note)
        
        for card in data['cards']:
            encrypted_card = card.copy()
            encrypted_card['card_number'] = self.encryption_manager.encrypt(card['card_number'])
            encrypted_card['cvv'] = self.encryption_manager.encrypt(card['cvv'])
            encrypted_card['notes'] = self.encryption_manager.encrypt(card['notes'])
            encrypted_data['cards'].append(encrypted_card)
        
        for identity in data['identities']:
            encrypted_identity = identity.copy()
            encrypted_identity['social_security_number'] = self.encryption_manager.encrypt(identity['social_security_number'])
            encrypted_identity['driver_license'] = self.encryption_manager.encrypt(identity['driver_license'])
            encrypted_identity['passport_number'] = self.encryption_manager.encrypt(identity['passport_number'])
            encrypted_identity['notes'] = self.encryption_manager.encrypt(identity['notes'])
            encrypted_data['identities'].append(encrypted_identity)
        
        for file in data['files']:
            encrypted_file = file.copy()
            encrypted_file['file_data'] = self.encryption_manager.encrypt(file['file_data'])
            encrypted_file['notes'] = self.encryption_manager.encrypt(file['notes'])
            encrypted_data['files'].append(encrypted_file)
        
        # Convert to JSON and encode
        json_data = json.dumps(encrypted_data, indent=2)
        
        # Create .lp file format with proprietary header
        lp_header = b"LUCKEEPASS_BACKUP_V1.0"
        lp_separator = b"\x00\xFF\x00\xFF"
        
        # Combine header, separator, and encrypted data
        lp_data = lp_header + lp_separator + json_data.encode('utf-8')
        
        return lp_data
    
    @staticmethod
    def get_backup_info(file_path: str) -> dict:
        """Get metadata from a LuckeePass backup file."""
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            
            lp_header = b"LUCKEEPASS_BACKUP_V1.0"
            lp_separator = b"\x00\xFF\x00\xFF"
            
            if not data.startswith(lp_header):
                raise ValueError("Invalid .lp file format")
            
            separator_pos = data.find(lp_separator)
            if separator_pos == -1:
                raise ValueError("Invalid .lp file format")
            
            json_start = separator_pos + len(lp_separator)
            if json_start >= len(data):
                raise ValueError("Invalid .lp file format. File too short.")
            
            try:
                json_data = data[json_start:].decode('utf-8')
            except UnicodeDecodeError:
                raise ValueError("Invalid .lp file format. Corrupted data encoding.")
            
            try:
                backup_data = json.loads(json_data)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid .lp file format. Corrupted JSON data: {str(e)}")
            
            # Verify app name
            if backup_data.get('app_name') != 'LuckeePass':
                raise ValueError("Invalid .lp file format. This file was not created by LuckeePass.")
            
            return {
                'app_name': backup_data.get('app_name', 'Unknown'),
                'company': backup_data.get('company', 'Unknown'),
                'version': backup_data.get('version', 'Unknown'),
                'created': backup_data.get('created', 'Unknown'),
                'password_count': len(backup_data.get('passwords', [])),
                'note_count': len(backup_data.get('notes', [])),
                'card_count': len(backup_data.get('cards', [])),
                'identity_count': len(backup_data.get('identities', [])),
                'file_count': len(backup_data.get('files', []))
            }
        except Exception as e:
            raise ValueError(f"Could not read backup file: {str(e)}")
    
    @staticmethod
    def is_valid_lp_file(file_path: str) -> bool:
        """Check if a file is a valid LuckeePass .lp backup file."""
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            
            lp_header = b"LUCKEEPASS_BACKUP_V1.0"
            return data.startswith(lp_header)
        except Exception:
            return False
    
    def import_data(self, lp_data: bytes) -> None:
        """Import data from .lp file format."""
        # Check for .lp file header
        lp_header = b"LUCKEEPASS_BACKUP_V1.0"
        lp_separator = b"\x00\xFF\x00\xFF"
        
        if not lp_data.startswith(lp_header):
            raise ValueError("Invalid .lp file format. This file was not created by LuckeePass.")
        
        # Find separator and extract JSON data
        separator_pos = lp_data.find(lp_separator)
        if separator_pos == -1:
            raise ValueError("Invalid .lp file format. Corrupted file.")
        
        json_start = separator_pos + len(lp_separator)
        if json_start >= len(lp_data):
            raise ValueError("Invalid .lp file format. File too short.")
        
        try:
            json_data = lp_data[json_start:].decode('utf-8')
        except UnicodeDecodeError:
            raise ValueError("Invalid .lp file format. Corrupted data encoding.")
        
        try:
            data = json.loads(json_data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid .lp file format. Corrupted JSON data: {str(e)}")
        
        # Verify app name
        if data.get('app_name') != 'LuckeePass':
            raise ValueError("Invalid .lp file format. This file was not created by LuckeePass.")
        
        # Get the salt from the data file and create a new encryption manager
        if 'encryption_salt' in data:
            import base64
            salt = base64.b64decode(data['encryption_salt'])
            # Create a new encryption manager with the salt from the data file
            from .encryption_manager import EncryptionManager
            self.encryption_manager = EncryptionManager(self.master_password, salt=salt)
        
        # Decrypt and load passwords
        self.passwords = []
        for entry_data in data.get('passwords', []):
            try:
                entry = entry_data.copy()
                entry['password'] = self.encryption_manager.decrypt(entry['password'])
                entry['notes'] = self.encryption_manager.decrypt(entry['notes'])
                self.passwords.append(PasswordEntry.from_dict(entry))
                self.categories.add(entry['category'])
            except Exception as e:
                print(f"Warning: Could not decrypt password entry '{entry_data.get('title', 'Unknown')}': {str(e)}")
                print(f"  This might be due to a different master password or corrupted data.")
                continue
        
        # Decrypt and load notes
        self.notes = []
        for note_data in data.get('notes', []):
            try:
                note = note_data.copy()
                note['content'] = self.encryption_manager.decrypt(note['content'])
                self.notes.append(SecureNote.from_dict(note))
                self.categories.add(note['category'])
            except Exception as e:
                print(f"Warning: Could not decrypt note '{note_data.get('title', 'Unknown')}': {str(e)}")
                print(f"  This might be due to a different master password or corrupted data.")
                continue
        
        # Decrypt and load cards
        self.cards = []
        for card_data in data.get('cards', []):
            try:
                card = card_data.copy()
                card['card_number'] = self.encryption_manager.decrypt(card['card_number'])
                card['cvv'] = self.encryption_manager.decrypt(card['cvv'])
                card['notes'] = self.encryption_manager.decrypt(card['notes'])
                self.cards.append(CardEntry.from_dict(card))
                self.categories.add(card['category'])
            except Exception as e:
                print(f"Warning: Could not decrypt card entry '{card_data.get('title', 'Unknown')}': {str(e)}")
                print(f"  This might be due to a different master password or corrupted data.")
                continue
        
        # Decrypt and load identities
        self.identities = []
        for identity_data in data.get('identities', []):
            try:
                identity = identity_data.copy()
                identity['social_security_number'] = self.encryption_manager.decrypt(identity['social_security_number'])
                identity['driver_license'] = self.encryption_manager.decrypt(identity['driver_license'])
                identity['passport_number'] = self.encryption_manager.decrypt(identity['passport_number'])
                identity['notes'] = self.encryption_manager.decrypt(identity['notes'])
                self.identities.append(IdentityEntry.from_dict(identity))
                self.categories.add(identity['category'])
            except Exception as e:
                print(f"Warning: Could not decrypt identity entry '{identity_data.get('title', 'Unknown')}': {str(e)}")
                print(f"  This might be due to a different master password or corrupted data.")
                continue
        
        # Decrypt and load files
        self.files = []
        for file_data in data.get('files', []):
            try:
                file = file_data.copy()
                # Decrypt the file data (it's stored as encrypted base64)
                encrypted_file_data = self.encryption_manager.decrypt(file['file_data'])
                file['file_data'] = encrypted_file_data  # This is now base64-encoded decrypted data
                file['notes'] = self.encryption_manager.decrypt(file['notes'])
                self.files.append(FileEntry.from_dict(file))
                self.categories.add(file['category'])
            except Exception as e:
                print(f"Warning: Could not decrypt file '{file_data.get('title', 'Unknown')}': {str(e)}")
                print(f"  This might be due to a different master password or corrupted data.")
                continue

    def clear_all_data(self) -> None:
        """Clear all passwords, notes, cards, and identities and save empty data."""
        self.passwords = []
        self.notes = []
        self.cards = []
        self.identities = []
        self.files = []
        self.categories = set()
        try:
            self.save_data()
        except Exception as e:
            print(f"Error clearing data: {str(e)}")

    @property
    def favorites(self):
        """Return a list of all favorited items with a type attribute for display in the favorites table."""
        favs = []
        for entry in self.passwords:
            if getattr(entry, 'is_favorite', False):
                entry.type = "Password"
                favs.append(entry)
        for note in self.notes:
            if getattr(note, 'is_favorite', False):
                note.type = "Secure Note"
                favs.append(note)
        for card in self.cards:
            if getattr(card, 'is_favorite', False):
                card.type = "Card"
                favs.append(card)
        for identity in self.identities:
            if getattr(identity, 'is_favorite', False):
                identity.type = "Identity"
                favs.append(identity)
        for file in self.files:
            if getattr(file, 'is_favorite', False):
                file.type = "File"
                favs.append(file)
        return favs 