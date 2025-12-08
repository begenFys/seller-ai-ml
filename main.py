import logging
from core.rag_agent import ask_agent
from core.embedding import get_embedding
from core.llm import generate_with_openrouter
from core.qdrant_search import client
from config.settings import OPENROUTER_API_KEY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_connection() -> bool:
    try:
        _ = get_embedding("test")
        logger.info("Эмбеддинг-модель доступна.")
    except Exception as e:
        logger.error(f"Ошибка эмбеддинг-модели: {e}")
        return False

    try:
        test_message = [{"role": "user", "content": "Привет, ответь коротко 'тест пройден'"}]
        response = generate_with_openrouter(test_message, max_tokens=10)
        logger.info(f"Генеративная модель работает: {response}")
    except Exception as e:
        logger.error(f"Ошибка генеративной модели: {e}")
        return False

    try:
        collections = client.get_collections()
        logger.info(f"Qdrant подключен, найдено коллекций: {len(collections.collections)}")
    except Exception as e:
        logger.error(f"Ошибка подключения к Qdrant: {e}")
        return False

    return True

def main():
    logger.info("RAG Агент LimeFitness (DeepSeek через OpenRouter)")
    logger.info("=" * 60)

    if not test_connection():
        logger.error("Не все сервисы доступны. Проверьте настройки.")
        exit(1)

    logger.info("Поиск будет выполняться по всем доступным коллекциям в Qdrant.")

    history = []

    while True:
        logger.info("\n" + "=" * 60)
        user_query = input("Ваш вопрос о фитнес-клубе (или 'quit' для выхода): ").strip()

        if user_query.lower() in ["quit", "exit", "выход", "q"]:
            logger.info("Работа завершена.")
            break

        if not user_query:
            continue

        try:
            answer = ask_agent(user_query, history)
            logger.info(f"\nОтвет агента:\n{'-'*40}\n{answer}\n{'-'*40}")

            history.append({"role": "user", "content": user_query})
            history.append({"role": "assistant", "content": answer})

            if len(history) > 10:
                history = history[-10:]
        except Exception as e:
            logger.error("Ошибка при обработке запроса", exc_info=True)
            print("Попробуйте повторить запрос или обратиться к менеджеру.")

if __name__ == "__main__":
    main()
