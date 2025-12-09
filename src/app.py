import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from src.core.rag_agent import ask_agent
from src.core.embedding import get_embedding
from src.core.llm import generate_with_openrouter
from src.core.qdrant_search import client
from src.config.settings import OPENROUTER_API_KEY
from models import QueryRequest, QueryResponse, HealthResponse

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создание FastAPI приложения
app = FastAPI(
    title="LimeFitness RAG Agent API",
    description="API для чат-бота фитнес-клуба LimeFitness",
    version="1.0.0"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "LimeFitness RAG Agent API"}

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Проверка состояния всех сервисов"""
    services = {}
    
    # Проверка эмбеддинг-модели
    try:
        _ = get_embedding("test")
        services["embedding"] = "healthy"
    except Exception as e:
        services["embedding"] = f"error: {str(e)}"
    
    # Проверка LLM
    try:
        test_message = [{"role": "user", "content": "Привет, ответь коротко 'тест пройден'"}]
        response = generate_with_openrouter(test_message, max_tokens=10)
        services["llm"] = "healthy"
    except Exception as e:
        services["llm"] = f"error: {str(e)}"
    
    # Проверка Qdrant
    try:
        collections = client.get_collections()
        services["qdrant"] = f"healthy, {len(collections.collections)} collections"
    except Exception as e:
        services["qdrant"] = f"error: {str(e)}"
    
    overall_status = "healthy" if all("healthy" in str(status) for status in services.values()) else "degraded"
    
    return HealthResponse(status=overall_status, services=services)

@app.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    """Обработка вопроса пользователя"""
    try:
        logger.info(f"Получен запрос: {request.query}")
        
        # Проверка входных данных
        if not request.query or not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Обработка запроса
        answer = ask_agent(request.query, request.history or [])
        
        return QueryResponse(
            answer=answer,
            success=True
        )
        
    except Exception as e:
        logger.error(f"Ошибка при обработке запроса: {e}", exc_info=True)
        return QueryResponse(
            answer="Произошла ошибка при обработке запроса",
            success=False,
            error=str(e)
        )

@app.post("/ask/stream")
async def ask_question_stream(request: QueryRequest):
    """Потоковая обработка вопроса (для будущей реализации)"""
    raise HTTPException(status_code=501, detail="Stream endpoint not implemented yet")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
