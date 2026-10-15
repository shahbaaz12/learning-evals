"""Load the grading model from the shared root environment."""

from dotenv import load_dotenv
from langchain_groq import ChatGroq

from models.config import MODEL_NAME, PROJECT_ROOT


def load_model():
    load_dotenv(PROJECT_ROOT.parent / ".env")
    model = ChatGroq(
        model=MODEL_NAME,
        temperature=0,
        reasoning_effort="low",
        max_tokens=1024,
        timeout=60,
    )
    return model.bind(response_format={"type": "json_object"})
