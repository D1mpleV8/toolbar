import os
import json
import base64
import time
from PyQt6.QtCore import QThread, pyqtSignal
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class ProfileEncryptionThread(QThread):
    """
    Background worker for local configuration profiles serialization & cryptographic encryption (FREE FEATURE).
    Generates a secure key from a user password using PBKDF2 KDF,
    then encrypts/decrypts the configuration JSON using AES-128 Fernet,
    completely preventing UI freeze frame drops.
    """
    op_completed = pyqtSignal(bool, str) # success, descriptive message
    profile_loaded = pyqtSignal(dict)    # Emits parsed dictionary on successful load
    status_msg = pyqtSignal(str)

    def __init__(self, mode: str, file_path: str, password: str, data_to_encrypt: dict = None):
        super().__init__()
        self.mode = mode # "ENCRYPT" or "DECRYPT"
        self.file_path = os.path.abspath(file_path)
        self.password = password
        self.data_to_encrypt = data_to_encrypt or {}

    def _derive_key(self) -> bytes:
        """Derives a cryptographically strong 32-byte Fernet key from the password."""
        # Use a hardcoded static salt for profile sync cross-compatibility.
        # In multi-system syncing, the salt must match across machines.
        salt = b"SteamPCToolboxPowerUserSuiteSalt"
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.password.encode('utf-8')))
        return key

    def run(self):
        self.status_msg.emit(f"Generating cryptographic keys from password...")
        time.sleep(0.3)

        try:
            key = self._derive_key()
            fernet = Fernet(key)

            if self.mode == "ENCRYPT":
                self.status_msg.emit("Serializing profile configuration database...")
                # Convert dictionary to JSON string
                json_data = json.dumps(self.data_to_encrypt, indent=4)

                self.status_msg.emit("Encrypting payload with AES-128 Fernet...")
                encrypted_bytes = fernet.encrypt(json_data.encode('utf-8'))

                self.status_msg.emit(f"Writing encrypted profile payload to disk: {os.path.basename(self.file_path)}")
                with open(self.file_path, "wb") as f:
                    f.write(encrypted_bytes)

                msg = f"Profile successfully encrypted & exported!"
                self.status_msg.emit(msg)
                self.op_completed.emit(True, msg)

            elif self.mode == "DECRYPT":
                if not os.path.exists(self.file_path):
                    self.op_completed.emit(False, "Target encrypted profile file does not exist.")
                    return

                self.status_msg.emit("Reading encrypted profile stream...")
                with open(self.file_path, "rb") as f:
                    encrypted_bytes = f.read()

                self.status_msg.emit("Decrypting payload...")
                decrypted_bytes = fernet.decrypt(encrypted_bytes)

                self.status_msg.emit("Deserializing config JSON structures...")
                profile_dict = json.loads(decrypted_bytes.decode('utf-8'))

                msg = "Profile successfully decrypted & imported!"
                self.status_msg.emit(msg)
                self.profile_loaded.emit(profile_dict)
                self.op_completed.emit(True, msg)

        except Exception as e:
            self.status_msg.emit(f"Cryptographic error: {str(e)}")
            self.op_completed.emit(False, f"Cryptographic operation failed: {str(e)}")
