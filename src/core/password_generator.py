"""
Password Generator
Handles password generation with various complexity options.
"""

import secrets
import string


class PasswordGenerator:
    """Handles password generation with various complexity options."""
    
    def __init__(self):
        self.lowercase = string.ascii_lowercase
        self.uppercase = string.ascii_uppercase
        self.digits = string.digits
        self.symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    def generate_password(self, length: int = 16, use_uppercase: bool = True,
                         use_digits: bool = True, use_symbols: bool = True,
                         exclude_similar: bool = True) -> str:
        """Generate a secure password with specified criteria."""
        chars = self.lowercase
        
        if use_uppercase:
            chars += self.uppercase
        if use_digits:
            chars += self.digits
        if use_symbols:
            chars += self.symbols
        
        if exclude_similar:
            # Remove similar characters
            chars = chars.replace('l', '').replace('1', '').replace('I', '')
            chars = chars.replace('O', '').replace('0', '')
            chars = chars.replace('S', '').replace('5', '')
        
        if len(chars) < length:
            raise ValueError("Character set too small for requested length")
        
        password = ''.join(secrets.choice(chars) for _ in range(length))
        
        # Ensure at least one character from each selected category
        if use_uppercase and not any(c in self.uppercase for c in password):
            password = secrets.choice(self.uppercase) + password[1:]
        if use_digits and not any(c in self.digits for c in password):
            password = secrets.choice(self.digits) + password[2:]
        if use_symbols and not any(c in self.symbols for c in password):
            password = secrets.choice(self.symbols) + password[3:]
        
        return password 