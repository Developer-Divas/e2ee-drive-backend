# chat/matcher.py

import re

INTENTS = [
        {
        "id": "GREETING",
        "priority": 1000,  # highest priority
        "phrases": [
            "hi",
            "hello",
            "hey",
            "how are you",
            "good morning",
            "good evening"
        ],
        "keywords": [],
        "weight": 0
    },
    {
        "id": "WRONG_PASSWORD",
        "priority": 100,
        "phrases": [
            "wrong password",
            "incorrect password",
            "password not working"
        ],
        "keywords": ["password", "decrypt", "decryption"],
        "weight": 5
    },
    {
        "id": "DOWNLOAD_FAILED",
        "priority": 80,
        "phrases": [
            "download failed",
            "file not opening",
            "cannot open file"
        ],
        "keywords": ["download", "open", "error"],
        "weight": 4
    },
    {
        "id": "RENAME_FILE",
        "priority": 60,
        "phrases": [
            "rename file",
            "change file name"
        ],
        "keywords": ["rename", "filename", "extension", "enc"],
        "weight": 3
    },
    {
        "id": "ENCRYPTION_FLOW",
        "priority": 40,
        "phrases": [
            "how encryption works",
            "how files are encrypted"
        ],
        "keywords": ["encrypt", "encryption", "aes", "secure"],
        "weight": 2
    },
    {
        "id": "SECURITY_TRUST",
        "priority": 30,
        "phrases": [
            "is my data safe",
            "can server read"
        ],
        "keywords": ["server", "privacy", "safe"],
        "weight": 2
    }
]

def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return text.strip()

def phrase_match(text: str, phrase: str) -> bool:
    return re.search(rf"\b{re.escape(phrase)}\b", text) is not None

def detect_intent(question: str) -> dict:
    text = normalize(question)

    # ---------- STAGE 1: GREETING ----------
    for intent in INTENTS:
        if intent["id"] == "GREETING":
            for phrase in intent["phrases"]:
                if phrase_match(text, phrase):
                    return {
                        "id": "GREETING",
                        "score": 10
                    }

    # ---------- STAGE 2: STRONG PHRASE MATCH ----------
    for intent in INTENTS:
        if intent["id"] == "GREETING":
            continue

        for phrase in intent["phrases"]:
            if phrase_match(text, phrase):
                return {
                    "id": intent["id"],
                    "score": 10
                }

    # ---------- STAGE 3: KEYWORD MATCH ----------
    best = {"id": "UNKNOWN", "score": 0}

    for intent in INTENTS:
        if intent["id"] == "GREETING":
            continue

        score = 0
        for keyword in intent["keywords"]:
            if keyword in text:
                score += intent["weight"]

        if score > best["score"]:
            best = {
                "id": intent["id"],
                "score": score
            }

    return best


def get_confidence(score: int) -> str:
    if score >= 10:
        return "high"
    if score >= 6:
        return "medium"
    return "low"
