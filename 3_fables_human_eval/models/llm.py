"""Connect the answer model to the shared root .env."""

from dotenv import load_dotenv
from langchain_groq import ChatGroq

from models.config import MODEL_NAME, PROJECT_ROOT


def load_model():
    load_dotenv(PROJECT_ROOT.parent / ".env")
    return ChatGroq(
        model=MODEL_NAME,
        temperature=0,
        reasoning_effort="low",
        max_tokens=512,
        timeout=60,
    )
