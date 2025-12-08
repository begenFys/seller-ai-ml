# core/llm.py
import requests
import json
from config.settings import GENERATION_MODEL, OPENROUTER_API_KEY
import logging

logger = logging.getLogger(__name__)

def generate_with_openrouter(messages: list, max_tokens: int = 500) -> str:
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://limefitness.club/",
                "X-Title": "LimeFitness Club",
            },
            data=json.dumps({
                "model": GENERATION_MODEL,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": 0.8,
                "top_p": 0.9
            }),
            timeout=30
        )

        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            logger.error(f"Ошибка OpenRouter API: {response.status_code} - {response.text}")
            return "Извините, произошла ошибка при генерации ответа."
    except Exception as e:
        logger.error(f"Ошибка при генерации текста: {e}")
        return "Извините, произошла ошибка при генерации ответа."
