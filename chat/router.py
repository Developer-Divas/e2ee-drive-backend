from fastapi import APIRouter
from pydantic import BaseModel

from .md_loader import load_markdown_files
from .matcher import match_doc

router = APIRouter(prefix="/chat", tags=["Garima"])

DOCS = load_markdown_files()

class ChatRequest(BaseModel):
    question: str

def build_help_list():
    lines = []
    for key in sorted(DOCS.keys()):
        lines.append(f"• {key.replace('_', ' ').title()}")
    return "\n".join(lines)

@router.post("/ask")
def ask_garima(payload: ChatRequest):
    doc = match_doc(payload.question, DOCS)

    if doc:
        return {
            "answer": doc.strip()
        }

    return {
        "answer": (
            "I couldn’t find this in the documentation.\n\n"
            "I can help you with:\n"
            f"{build_help_list()}"
        )
    }
