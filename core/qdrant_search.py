# core/qdrant_search.py
from qdrant_client import QdrantClient
from qdrant_client.http.models import ScoredPoint
from core.embedding import get_embedding
from config.settings import QDRANT_URL, API_KEY
import logging

logger = logging.getLogger(__name__)
client = QdrantClient(url=QDRANT_URL, api_key=API_KEY)

def search_context(query: str, top_k: int = 5) -> list:
    try:
        query_vector = get_embedding(query)
        if not query_vector:
            logger.warning("Не удалось получить эмбеддинг для запроса.")
            return []

        collections = client.get_collections()
        all_collections = [col.name for col in collections.collections]
        all_hits = []

        for collection_name in all_collections:
            try:
                hits = client.search(
                    collection_name=collection_name,
                    query_vector=query_vector,
                    limit=top_k,
                    score_threshold=0.6,
                    with_payload=True
                )
                for h in hits:
                    if isinstance(h.payload, dict):
                        h.payload.setdefault("__collection", collection_name)
                all_hits.extend(hits)
            except Exception as e:
                logger.error(f"Ошибка при поиске в коллекции {collection_name}: {e}")

        all_hits.sort(key=lambda x: x.score or 0.0, reverse=True)
        return all_hits[:top_k]
    except Exception as e:
        logger.error(f"Ошибка при поиске контекста: {e}")
        return []
