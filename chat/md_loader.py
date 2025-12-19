import os

BASE_DIR = os.path.dirname(__file__)
KNOWLEDGE_DIR = os.path.join(BASE_DIR, "knowledge")

def load_markdown_files():
    docs = {}

    if not os.path.exists(KNOWLEDGE_DIR):
        return docs

    for filename in os.listdir(KNOWLEDGE_DIR):
        if filename.endswith(".md"):
            key = filename.replace(".md", "").lower()
            path = os.path.join(KNOWLEDGE_DIR, filename)

            with open(path, "r", encoding="utf-8") as f:
                docs[key] = f.read()

    return docs
