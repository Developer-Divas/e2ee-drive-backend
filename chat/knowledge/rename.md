# File Behavior

## Upload
• File is encrypted first
• Encrypted file is stored with `.enc` extension
• Metadata is stored separately
• Original filename is preserved in metadata

## Download
• Encrypted file is downloaded
• Browser decrypts file locally
• Original filename is restored after decryption

## Rename
• Only the filename (not content) is renamed
• File remains encrypted after rename
• Extension `.enc` is locked and cannot be removed

## Delete
• Deletes file from storage
• Removes metadata from database
• Operation is permanent
