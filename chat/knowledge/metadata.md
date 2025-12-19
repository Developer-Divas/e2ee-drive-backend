# Encryption Metadata

Each encrypted file has metadata stored separately.

## Metadata contains
• iv (initialization vector)
• salt (used for key derivation)
• original file name
• mime type
• file size
• encryption algorithm

## Metadata purpose
• Required for decryption
• Does not contain password
• Safe to store on server

## Example
Metadata alone cannot decrypt a file.
Password is still required.
