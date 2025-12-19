# Password Handling

Passwords are used only for encryption and decryption.

## During upload
• User enters a password
• Password is used to derive an encryption key
• Password is never sent to the backend
• Password is never stored

## During download
• User must enter the same password
• Wrong password results in decryption failure
• Server does not validate passwords

## Important
Passwords are not recoverable.
If a password is lost, the encrypted file is lost permanently.
