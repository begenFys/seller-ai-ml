# utils/helpers.py
import re

def clean_output(text: str) -> str:
    """Удаляет markdown-форматирование и служебные фразы из ответа модели."""
    if not text:
        return text

    text = re.sub(r"[*`_#>~]+", "", text)
    text = re.sub(r'\r', '', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]{2,}', ' ', text)
    return text.strip()

def truncate_context(context: str, max_chars: int = 3000) -> str:
    return context[:max_chars] if len(context) > max_chars else context

def format_contexts(contexts: list) -> str:
    parts = []
    for point in contexts:
        txt = ""
        try:
            txt = point.payload.get("text", "")
        except Exception:
            try:
                txt = str(point.payload)
            except Exception:
                txt = ""
        if txt:
            parts.append(txt)
    return "\n\n".join(parts)
