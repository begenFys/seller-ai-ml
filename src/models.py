from pydantic import BaseModel
from typing import List, Optional

class QueryRequest(BaseModel):
    query: str
    history: Optional[List[dict]] = []

class QueryResponse(BaseModel):
    answer: str
    success: bool
    error: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    services: dict
