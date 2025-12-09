# config/settings.py
import os
from dotenv import load_dotenv

load_dotenv()

# Qdrant
QDRANT_URL = os.getenv("QDRANT_URL")
API_KEY = os.getenv("API_KEY")

# Embedding
EMBEDDING_MODEL = "intfloat/multilingual-e5-large-instruct"

# LLM
GENERATION_MODEL = "deepseek/deepseek-chat-v3-0324"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Validation
if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "your_openrouter_api_key_here":
    raise ValueError("OPENROUTER_API_KEY не задан в .env")
