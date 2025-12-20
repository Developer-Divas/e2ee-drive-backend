# chat/router.py

from fastapi import APIRouter
from pydantic import BaseModel

from .matcher import detect_intent, get_confidence
from .md_loader import load_markdown

router = APIRouter(prefix="/chat", tags=["Garima"])


class ChatRequest(BaseModel):
    question: str


# 🔹 SHORT ANSWERS (PRIMARY CHAT RESPONSE)
SHORT_ANSWERS = {
    "GREETING": (
        "Hi 👋 I’m Garima.\n\n"
        "I can help you with:\n"
        "• Encryption & security\n"
        "• Password & decryption issues\n"
        "• File & folder behavior\n\n"
        "Ask me anything 🙂"
    ),

    "WRONG_PASSWORD": (
        "If the password is wrong, the file cannot be decrypted.\n\n"
        "Make sure you use the **same password used during upload**."
    ),

    "DOWNLOAD_FAILED": (
        "If a file won’t open after download, it’s usually due to:\n"
        "• Wrong password\n"
        "• Renaming the file incorrectly\n"
        "• Interrupted download"
    ),

    "RENAME_FILE": (
        "You can rename files, but the **.enc extension is locked**.\n"
        "Only the file name can be changed."
    ),

    "ENCRYPTION_FLOW": (
        "Files are encrypted **in your browser** using AES-256-GCM.\n"
        "The password never leaves your device."
    ),

    "SECURITY_TRUST": (
        "Your data is secure.\n"
        "• Encryption happens in your browser\n"
        "• Server stores only encrypted files\n"
        "• Passwords are never sent or stored"
    ),
}


def summarize_markdown(md: str, max_lines: int = 6) -> str:
    """
    Trim markdown to avoid dumping full documentation.
    """
    lines = [
        line for line in md.split("\n")
        if line.strip() and not line.strip().startswith("#")
    ]
    return "\n".join(lines[:max_lines])


@router.post("/ask")
def ask_garima(payload: ChatRequest):
    question = payload.question.strip()
    print("question:", question)

    if not question:
        return {
            "answer": "Please ask a question 🙂",
            "confidence": "high"
        }

    intent = detect_intent(question)
    print("intent:", intent)

    confidence = get_confidence(intent["score"])
    print("confidence:", confidence)

    intent_id = intent["id"]

    # ✅ PRIMARY SHORT ANSWER
    short_answer = SHORT_ANSWERS.get(
        intent_id,
        "I’m not fully sure about that yet, but I’ll try to help 🙂"
    )

    # ✅ OPTIONAL LONG EXPLANATION (TRIMMED)
    md_content = load_markdown(intent_id)
    long_answer = None

    if md_content:
        long_answer = summarize_markdown(md_content)

        if confidence == "medium":
            long_answer = "🤔 This might help:\n\n" + long_answer
        elif confidence == "low":
            long_answer = "I’m not fully sure, but this may be useful:\n\n" + long_answer

    return {
        "answer": short_answer,        # 👈 what Garima says
        "details": long_answer,        # 👈 optional deeper explanation
        "confidence": confidence,
        "intent": intent_id
    }
