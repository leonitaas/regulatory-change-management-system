import os
from dotenv import load_dotenv


load_dotenv()


def get_groq_api_key() -> str | None:
    return os.getenv("GROQ_API_KEY")


def get_groq_model() -> str:
    return os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")