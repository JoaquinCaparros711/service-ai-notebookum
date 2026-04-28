import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    GEMMA_API_KEY = os.environ.get("GEMMA_API_KEY")
    GEMMA_API_URL = os.environ.get("GEMMA_API_URL")
