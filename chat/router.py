from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/chat", tags=["Garima"])

class ChatRequest(BaseModel):
    question: str

@router.post("/ask")
def ask_garima(payload: ChatRequest):
    q = payload.question.lower()

    # ---- BASIC INTELLIGENCE (PROJECT AWARE) ----
    if "encrypt" in q or "encryption" in q:
        return {
            "answer": (
                "Your files are encrypted in the browser using AES-256-GCM. "
                "The password never leaves your device, and the server cannot decrypt your files."
            )
        }

    if "password" in q:
        return {
            "answer": (
                "Each file can have its own password. "
                "Passwords are never stored or sent to the server."
            )
        }

    if "rename" in q:
        return {
            "answer": (
                "File renaming only changes metadata and storage paths. "
                "Encryption remains unchanged."
            )
        }

    if "server" in q:
        return {
            "answer": (
                "The server only stores encrypted blobs and metadata. "
                "It has no access to decryption keys."
            )
        }

    # ---- FALLBACK ----
    return {
        "answer": (
            "I am Garima 👋\n\n"
            "I can help you understand how this E2EE Drive works:\n"
            "• Encryption & decryption\n"
            "• Password handling\n"
            "• File & folder behavior\n"
            "• Security guarantees\n\n"
            "Ask me anything related to this project."
        )
    }
