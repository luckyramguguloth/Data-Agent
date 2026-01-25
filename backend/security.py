import os
from cryptography.fernet import Fernet
import logging

logger = logging.getLogger(__name__)

class SecurityManager:
    def __init__(self, key_path="secret.key"):
        self.key_path = key_path
        self.key = self._load_or_generate_key()
        self.cipher = Fernet(self.key)

    def _load_or_generate_key(self):
        """Loads the key from a file or generates a new one if it doesn't exist."""
        if os.path.exists(self.key_path):
            with open(self.key_path, "rb") as key_file:
                return key_file.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_path, "wb") as key_file:
                key_file.write(key)
            logger.info(f"New encryption key generated at {self.key_path}")
            return key

    def encrypt_data(self, data: bytes) -> bytes:
        """Encrypts bytes data."""
        return self.cipher.encrypt(data)

    def decrypt_data(self, token: bytes) -> bytes:
        """Decrypts bytes data."""
        return self.cipher.decrypt(token)

    def encrypt_file(self, file_path):
        """Encrypts a file in place."""
        try:
            with open(file_path, "rb") as f:
                data = f.read()
            encrypted_data = self.encrypt_data(data)
            with open(file_path, "wb") as f:
                f.write(encrypted_data)
        except Exception as e:
            logger.error(f"Encryption failed for {file_path}: {e}")
            raise e

    def decrypt_file_to_memory(self, file_path) -> bytes:
        """Decrypts a file and returns bytes (does not write to disk)."""
        try:
            with open(file_path, "rb") as f:
                encrypted_data = f.read()
            return self.decrypt_data(encrypted_data)
        except Exception as e:
            logger.error(f"Decryption failed for {file_path}: {e}")
            raise e
