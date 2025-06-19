"""
Encryption Manager
Handles encryption and decryption of sensitive data.
"""

import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from typing import Optional


class EncryptionManager:
    """Handles encryption and decryption of sensitive data."""
    
    def __init__(self, master_password: str, salt: Optional[bytes] = None):
        self.master_password = master_password.encode()
        self.salt = salt if salt is not None else os.urandom(16)  # Use provided salt or generate new one

        self.key = self._derive_key()
        self.cipher = Fernet(self.key)
    
    def _derive_key(self) -> bytes:
        """Derive encryption key from master password."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(self.master_password))
    
    def get_salt(self) -> bytes:
        """Return the salt used for key derivation."""
        return self.salt
    
    def encrypt(self, data: str) -> str:
        """Encrypt data."""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt data."""
        return self.cipher.decrypt(encrypted_data.encode()).decode() 