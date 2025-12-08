# core/rag_agent.py
from core.qdrant_search import search_context
from core.llm import generate_with_openrouter
from utils.helpers import clean_output, format_contexts, truncate_context
import logging

logger = logging.getLogger(__name__)

def ask_agent(query: str, history: list) -> str:
    logger.info(f"Запрос: {query}")

    contexts = search_context(query, top_k=5)
    if not contexts:
        return "К сожалению, подходящая информация не найдена. Рекомендуем обратиться к менеджеру клуба для уточнения."

    context_text = format_contexts(contexts)
    context_text = truncate_context(context_text)

    system_prompt = (
        "Вы — Дмитрий, дружелюбный и внимательный консультант фитнес-клуба LimeFitness. "
        "Отвечайте как опытный сотрудник, который заботится о клиенте. "
        "Говорите просто, без лишней официальности, как в обычной беседе. "
        "Если не знаете — честно скажите. "
        "Отвечайте на том же языке на котором был задан вопрос. "
        "Используйте только информацию из контекста. "
        "Не отвечайте на воросы касающиеся религии или политики. "
        "Отвечайте с душой. Помните, что вы помогаете человеку выбрать здоровье и активность."
    )

    messages = [{"role": "system", "content": system_prompt}] + history + [
        {"role": "user", "content": f"Контекст:\n{context_text}\n\nВопрос: {query}"}
    ]

    logger.info("Генерация ответа...")
    raw_answer = generate_with_openrouter(messages)
    answer = clean_output(raw_answer)

    if not answer:
        return "Извините, по данному вопросу недостаточно информации. Рекомендуем связаться с менеджером клуба для уточнения."

    return answer
