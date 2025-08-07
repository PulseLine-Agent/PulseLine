import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")

LLM_CONFIG = {
    "temperature": 1.0,
    "max_tokens": 512,
    "top_p": 1,
    "stream": True,
    "stop": None,
}

HOST = "0.0.0.0"
PORT = 5050

USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
DATABASE = os.getenv("DATABASE")
HOST = os.getenv("HOST")