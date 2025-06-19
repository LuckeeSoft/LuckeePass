"""
User Manager
Handles user authentication and master password management.
"""

import os
import bcrypt
from typing import Optional, Dict, List
from src.utils.resource_path import get_appdata_path


class UserManager:
    """Handles user authentication and master password management."""
    
    def __init__(self):
        self.hashed_master_password = None
        self.vault_salt = None
        
        # File paths
        self.master_password_file = get_appdata_path("luckeepass_master.dat")
        self.vault_salt_file = get_appdata_path("luckeepass_vault_salt.dat")
        
        # Load existing data
        self.hashed_master_password = self._load_master_password_hash()
        self.vault_salt = self._load_vault_salt()
    
    def _load_master_password_hash(self) -> Optional[bytes]:
        """Load the master password hash from file."""
        if os.path.exists(self.master_password_file):
            try:
                with open(self.master_password_file, 'rb') as f:
                    return f.read()
            except Exception as e:
                print(f"Error loading master password hash: {e}")
        return None

    def _save_master_password_hash(self, hashed_password: bytes) -> None:
        """Save the master password hash to file."""
        try:
            with open(self.master_password_file, 'wb') as f:
                f.write(hashed_password)
        except Exception as e:
            print(f"Error saving master password hash: {e}")

    def _load_vault_salt(self) -> Optional[bytes]:
        """Load the vault salt from file."""
        if os.path.exists(self.vault_salt_file):
            try:
                with open(self.vault_salt_file, 'rb') as f:
                    return f.read()
            except Exception as e:
                print(f"Error loading vault salt: {e}")
        return None

    def _save_vault_salt(self, salt: bytes) -> None:
        """Save the vault salt to file."""
        try:
            with open(self.vault_salt_file, 'wb') as f:
                f.write(salt)
            self.vault_salt = salt
        except Exception as e:
            print(f"Error saving vault salt: {e}")

    def set_master_password(self, master_password: str) -> None:
        """Set the master password."""
        hashed = bcrypt.hashpw(master_password.encode(), bcrypt.gensalt())
        self._save_master_password_hash(hashed)

        # Generate a new vault salt if one doesn't exist
        if self.vault_salt is None:
            import os
            new_salt = os.urandom(16)
            self._save_vault_salt(new_salt)

    def verify_master_password(self, master_password: str) -> bool:
        """Verify the master password."""
        if not self.hashed_master_password:
            return False  # No master password set yet
        try:
            return bcrypt.checkpw(master_password.encode(), self.hashed_master_password)
        except ValueError as e:
            print(f"Warning: Stored master password hash is invalid: {e}. Please reset your password.")
            return False

    def get_vault_salt(self) -> Optional[bytes]:
        """Get the vault salt for encryption."""
        return self.vault_salt

    def is_master_password_set(self) -> bool:
        """Check if a master password has been set."""
        return self.hashed_master_password is not None 

    def delete_user_data(self):
        """Delete all user data files (master password, vault salt, and vault data)."""
        import os
        try:
            if os.path.exists(self.master_password_file):
                os.remove(self.master_password_file)
            if os.path.exists(self.vault_salt_file):
                os.remove(self.vault_salt_file)
            # Optionally, delete the main vault data file as well
            lp_path = get_appdata_path("luckeepass_data.lp")
            if os.path.exists(lp_path):
                os.remove(lp_path)
        except Exception as e:
            print(f"Error deleting user data: {e}")
            raise 