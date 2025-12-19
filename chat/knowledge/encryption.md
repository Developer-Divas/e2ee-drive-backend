# Encryption

All files are encrypted in the browser before upload.

The encryption algorithm used is **AES-256-GCM**, which is an industry-standard authenticated encryption method.

## How encryption works
• File is encrypted on the client (browser)
• Password is used to derive a cryptographic key
• Encrypted bytes are uploaded to the server
• Server never sees the password or key

## Important facts
• Password never leaves the browser
• Server cannot decrypt files
• Even admins cannot access file contents
• Without the password, files are permanently unreadable

## Security note
If you forget the password, the file cannot be recovered.
