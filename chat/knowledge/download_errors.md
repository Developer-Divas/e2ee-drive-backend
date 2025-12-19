# Download & Decryption

Downloading a file is a two-step process: download and decrypt.

## Step 1: Download
• Server provides a signed URL
• Encrypted file is downloaded as-is
• Server does not modify file content
• File remains encrypted at this stage

## Step 2: Decryption
• User enters encryption password
• Browser derives the decryption key
• File is decrypted locally in the browser
• Original file name is restored

## Wrong password behavior
• Decryption fails immediately
• No corrupted file is produced
• User is prompted to try again
• Server is not involved in password validation

## Important notes
• Download works from any device
• Password must be the same as upload
• Without password, file cannot be opened
• Server cannot help recover files

## Security guarantee
Even if the server is compromised, downloaded files remain encrypted.
