PROJECT_KNOWLEDGE = """
This project is an End-to-End Encrypted (E2EE) Drive.

Files are encrypted in the browser using AES-256-GCM before upload.
Passwords never leave the user’s device.
The server stores only encrypted files and cannot decrypt them.

Encrypted files are stored with a .enc extension.
The original filename is stored separately in encrypted metadata.

Renaming a file changes the encrypted filename but preserves the original name.
If a password is lost, files cannot be recovered.

The system follows a zero-knowledge security model.
"""
