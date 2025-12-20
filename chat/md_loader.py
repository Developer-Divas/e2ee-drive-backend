# chat/md_loader.py

import os

BASE_DIR = os.path.dirname(__file__)
KNOWLEDGE_DIR = os.path.join(BASE_DIR, "knowledge")

INTENT_FILE_MAP = {
    "WRONG_PASSWORD": "password.md",
    "DOWNLOAD_FAILED": "download.md",
    "ENCRYPTION_FLOW": "encryption.md",
    "RENAME_FILE": "rename.md",
    "SECURITY_TRUST": "security.md"
}


def load_markdown(intent_id: str) -> str:
    print("intent_id : ",intent_id)
    
    filename = INTENT_FILE_MAP.get(intent_id)
    print("filename : ",filename)
    print("KNOWLEDGE_DIR : ",KNOWLEDGE_DIR)

    if not filename:
        return None

    path = os.path.join(KNOWLEDGE_DIR, filename)

    if not os.path.exists(path):
        return None

    with open(path, "r", encoding="utf-8") as f:
        return f.read()
