# core/embedding.py
from sentence_transformers import SentenceTransformer
from src.config.settings import EMBEDDING_MODEL
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)
embedding_model = SentenceTransformer(EMBEDDING_MODEL)

@lru_cache(maxsize=128)
def get_embedding_cached(text: str) -> tuple:
    try:
        return tuple(embedding_model.encode(text).tolist())
    except Exception as e:
        logger.error(f"Ошибка при создании эмбеддинга: {e}")
        return tuple()

def get_embedding(text: str) -> list:
    try:
        return embedding_model.encode(text).tolist()
    except Exception as e:
        logger.error(f"Ошибка при создании эмбеддинга: {e}")
        return []
