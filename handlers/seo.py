import requests
from bs4 import BeautifulSoup

from config import bot, TELEGRAM_TOKEN
from prompts import PROMPTS
from bot_ui.states import user_styles, user_info, waiting_for_link
from bot_ui.keyboards import get_seo_keyboard, get_smm_keyboard, get_translate_inline_keyboard
from storage.user_store import save_user, check_limit, increment_count
from utils.formatting import format_text, send_long_message
from ai.router import generate_text, generate_multimodal


@bot.message_handler(func=lambda m: m.text == "🚀 SEO инструменты")
def seo_menu(message):
    bot.send_message(message.chat.id, "Выберите SEO-инструмент для работы:", reply_markup=get_seo_keyboard())


@bot.message_handler(func=lambda m: m.text == "📍 Собрать ключи")
def seo_keys_handler(message):
    user_styles[message.from_user.id] = "seo_keys"
    bot.send_message(message.chat.id, "🎯 Режим: <b>Сбор ключевых слов</b>.\nТеперь отправь фото товара.", parse_mode="HTML")


@bot.message_handler(func=lambda m: m.text == "🏷 Мета-теги (T/D)")
def seo_meta_handler(message):
    user_styles[message.from_user.id] = "seo_meta"
    bot.send_message(message.chat.id, "🏷 Режим: <b>Meta-теги (Title/Description)</b>.\nТеперь отправь фото товара.", parse_mode="HTML")


@bot.message_handler(func=lambda m: m.text == "✌️ Рерайт по ссылке")
def rewrite_link_handler(message):
    waiting_for_link.add(message.from_user.id)
    bot.send_message(message.chat.id, "🔗 Пришли ссылку на страницу товара для рерайта.")


@bot.message_handler(func=lambda m: m.text == "💰 Анализ цен")
def price_handler(message):
    user_styles[message.from_user.id] = "price_analysis"
    bot.send_message(message.chat.id, "💰 Режим: <b>Анализ цен</b>. Отправь фото товара.", parse_mode="HTML")


@bot.message_handler(func=lambda m: m.from_user.id in waiting_for_link)
def process_rewrite(message):
    url = message.text
    waiting_for_link.discard(message.from_user.id)

    if not url.startswith("http"):
        bot.reply_to(message, "❌ Это не ссылка. Попробуй нажать на кнопку ещё раз.")
        return

    bot.reply_to(message, "⏳ Читаю сайт...")
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        for s in soup(["script", "style"]):
            s.extract()

        clean_text = " ".join(soup.get_text().split())[:3000]
        prompt = (
            f"Сделай уникальный SEO-рерайт описания люстры или светильника по этому тексту. "
            f"Не перегружай текст, максимум 150 слов. "
            f"Без спецсимволов и эмодзи: {clean_text}"
        )
        result = generate_text(prompt)
        send_long_message(message.chat.id, format_text(result))
    except Exception:
        bot.reply_to(message, "⚠️ Не удалось прочитать сайт. Возможно, он защищён.")


@bot.message_handler(content_types=["photo"])
def handle_photo(message):
    save_user(message.from_user)

    if not check_limit(message):
        return

    increment_count(message.from_user.id)
    bot.reply_to(message, "⏳ Обрабатываю фото...")

    try:
        style = user_styles.get(message.from_user.id, "detailed")
        extra_info = user_info.get(message.from_user.id, "")
        caption = message.caption or ""

        prompt = PROMPTS.get(style, PROMPTS["detailed"]).replace("{{user_specs}}", extra_info)
        if caption:
            prompt += f"\n\nДополнительные указания: {caption}"

        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_info.file_path}"
        img_content = requests.get(file_url, timeout=30).content

        if style == "smm_ideas":
            prompt = PROMPTS[style] + f"\n\nТема пользователя: {caption or 'товар на фото'}\nСделай идеи конкретными, цепкими и готовыми к публикации."

        result = generate_multimodal(prompt, img_content)
        text = format_text(result)

        if len(text) > 4000:
            send_long_message(message.chat.id, text)
            bot.send_message(
                message.chat.id,
                "⬆️ Текст отправлен частями.",
            )
        else:
            bot.send_message(
                message.chat.id,
                text,
                parse_mode="HTML",
            )

        if style in ["smm_reels", "smm_stories", "smm_ideas", "social"]:
            bot.send_message(message.chat.id, "📸 Готово! Можешь прислать ещё фото для SMM.", reply_markup=get_smm_keyboard())
        else:
            bot.send_message(message.chat.id, "🚀 Готово! Жду следующее фото для SEO.", reply_markup=get_seo_keyboard())

    except Exception as e:
        error_text = str(e)
        print(f"ОШИБКА В handle_photo: {error_text}")

        if "503" in error_text or "UNAVAILABLE" in error_text or "high demand" in error_text:
            bot.reply_to(message, "⏳ Нейросеть сейчас перегружена — слишком много запросов. Подожди 1-2 минуты и попробуй снова.")
        elif "RESOURCE_EXHAUSTED" in error_text or "429" in error_text:
            bot.reply_to(message, "⏳ Лимит запросов к нейросети временно исчерпан. Попробуй через пару минут.")
        elif "Все провайдеры" in error_text:
            bot.reply_to(message, "⚠️ Все нейросети для обработки фото сейчас недоступны. Попробуй позже.")
        else:
            bot.reply_to(message, "⚠️ Что-то пошло не так при обработке фото. Попробуй ещё раз.")
