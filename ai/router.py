from io import BytesIO

import requests
from PIL import Image

from config import (
    GROQ_API_KEY,
    OPENROUTER_API_KEY,
    GEMINI_API_KEY,
    DEEPSEEK_API_KEY,
    gemini_client,
)

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"


def _deepseek_text(prompt: str) -> str:
    if not DEEPSEEK_API_KEY:
        raise RuntimeError("DEEPSEEK_API_KEY не задан")

    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.4,
    }
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }
    response = requests.post(DEEPSEEK_URL, json=payload, headers=headers, timeout=60)
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]


def _groq_text(prompt: str) -> str:
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY не задан")

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.4,
    }
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    response = requests.post(GROQ_URL, json=payload, headers=headers, timeout=60)
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]


def _openrouter_text(prompt: str) -> str:
    if not OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY не задан")

    payload = {
        "model": "meta-llama/llama-3.1-8b-instruct:free",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.4,
    }
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    response = requests.post(OPENROUTER_URL, json=payload, headers=headers, timeout=60)
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]


def _gemini_text(prompt: str) -> str:
    if not gemini_client:
        raise RuntimeError("GEMINI_API_KEY не задан")
    result = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[prompt]
    )
    return getattr(result, "text", "") or ""


def _gemini_multimodal(prompt: str, image_bytes: bytes) -> str:
    if not gemini_client:
        raise RuntimeError("GEMINI_API_KEY не задан")

    img = Image.open(BytesIO(image_bytes))
    img.load()
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGB")
    max_size = 1600
    if img.width > max_size or img.height > max_size:
        img.thumbnail((max_size, max_size))

    result = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[prompt, img]
    )
    return getattr(result, "text", "") or ""


def generate_text(prompt: str) -> str:
    """
    Порядок: DeepSeek → Groq → OpenRouter → Gemini
    Используется для всех текстовых задач (посты, SEO, менеджер).
    """
    providers = []
    if DEEPSEEK_API_KEY:
        providers.append(("DeepSeek", _deepseek_text))
    if GROQ_API_KEY:
        providers.append(("Groq", _groq_text))
    if OPENROUTER_API_KEY:
        providers.append(("OpenRouter", _openrouter_text))
    if GEMINI_API_KEY:
        providers.append(("Gemini", _gemini_text))

    if not providers:
        raise RuntimeError("Не задан ни один API ключ для текстовой генерации")

    last_error = None
    for name, provider in providers:
        try:
            text = provider(prompt).strip()
            if text:
                print(f"[router] Текст сгенерирован через {name}")
                return text
        except Exception as e:
            print(f"[router] {name} недоступен: {e}")
            last_error = e
            continue

    raise last_error or RuntimeError("Не удалось получить ответ от текстовой модели")


def generate_multimodal(prompt: str, image_bytes: bytes) -> str:
    """
    Фото всегда через Gemini — он лучший для мультимодала.
    Если Gemini недоступен — fallback на текст без фото.
    """
    if GEMINI_API_KEY:
        return _gemini_multimodal(prompt, image_bytes)
    return generate_text(prompt + "\n\n[Фото не обработано: Gemini не настроен]")