# Security Model

This system follows a **zero-knowledge architecture**.

## What the server knows
• Encrypted file bytes
• File size
• Metadata (non-secret)

## What the server does NOT know
• Passwords
• Encryption keys
• File contents

## Trust model
• Client is trusted
• Server is untrusted
• Security does not depend on backend secrecy
