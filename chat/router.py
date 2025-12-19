# chat/router.py

from fastapi import APIRouter
from pydantic import BaseModel

from .matcher import detect_intent, get_confidence
from .md_loader import load_markdown

router = APIRouter(prefix="/chat", tags=["Garima"])


class ChatRequest(BaseModel):
    question: str


@router.post("/ask")
def ask_garima(payload: ChatRequest):
    question = payload.question.strip()
    print("question :", question)
    
    if not question:
        return {
            "answer": "Please ask a question 🙂"
        }

    intent = detect_intent(question)
    print("intent :", intent)

    confidence = get_confidence(intent["score"])
    print("confidence :", confidence)

    if intent["id"] == "GREETING":
        return {
            "answer": (
                "Hi 👋 I’m Garima.\n\n"
                "I can help you with:\n"
                "• Encryption & security\n"
                "• Password & decryption issues\n"
                "• File & folder behavior\n\n"
                "Ask me anything 🙂"
            ),
            "confidence": "high"
        }

    content = load_markdown(intent["id"])

    if not content:
        return {
            "answer": (
                "I couldn’t find this in the documentation.\n\n"
                "You can ask about:\n"
                "• Encryption & security\n"
                "• Password handling\n"
                "• File & folder behavior\n"
                "• Download & decryption errors"
            )
        }

    # 🔐 Confidence-aware prefix
    if confidence == "medium":
        content = (
            "🤔 I think this might be related to this:\n\n"
            + content
        )
    elif confidence == "low":
        content = (
            "I’m not fully sure, but this might help:\n\n"
            + content
        )

    return {
        "answer": content,
        "confidence": confidence
    }
