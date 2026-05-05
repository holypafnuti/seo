from config import bot
from prompts import PROMPTS
from bot_ui.states import user_styles, waiting_for_topic, waiting_for_smm
from bot_ui.keyboards import get_smm_keyboard, get_main_keyboard
from storage.user_store import check_limit, increment_count
from utils.formatting import format_text, send_long_message
from ai.router import generate_text


@bot.message_handler(func=lambda m: m.text == "📱 SMM инструменты")
def smm_menu(message):
    bot.send_message(message.chat.id, "Выбери SMM-инструмент:", reply_markup=get_smm_keyboard())


@bot.message_handler(func=lambda m: m.text == "📱 Пост по фото")
def social_photo_handler(message):
    user_styles[message.from_user.id] = "social"
    bot.reply_to(message, "Отправь фото товара — напишу пост для соцсетей 👇")


@bot.message_handler(func=lambda m: m.text == "✌️ Пост по теме")
def topic_post_handler(message):
    waiting_for_topic.add(message.from_user.id)
    bot.reply_to(
        message,
        "Напиши тему или ключевые слова для поста.\n\n"
        "Например: <code>люстра в скандинавском стиле для гостиной</code>",
        parse_mode="HTML"
    )


@bot.message_handler(func=lambda m: m.from_user.id in waiting_for_topic)
def generate_topic_post(message):
    waiting_for_topic.discard(message.from_user.id)

    if not check_limit(message):
        return

    increment_count(message.from_user.id)
    bot.reply_to(message, "⏳ Пишу пост...")

    try:
        prompt = (
            f"Ты — SMM-копирайтер магазина люстр и светильников. "
            f"Напиши продающий пост для Instagram/VK на тему: {message.text}\n"
            f"Формат строго:\n"
            f"ПОСТ: живой текст 2-3 предложения, цепляющий первый абзац, с провокационным хуком, без штампов, "
            f"текст должен вызывать противоречивые эмоции, желание поспорить в комментариях, должен восприниматься легко.\n"
            f"Никаких хэштегов, стиль текста живой, приятельский, никаких мы и обращения на вы, "
            f"если есть побуждение к действию, то через личное обращение.\n"
            f"Запрещено: заголовки, по типу 'Пост:', 'Хэштеги:', *, # в тексте поста, маркеры, эмодзи."
        )
        text = format_text(generate_text(prompt))
        send_long_message(message.chat.id, text, reply_to=message)
    except Exception as e:
        print(f"ОШИБКА: {str(e)}")
        bot.reply_to(message, f"Ошибка: {str(e)}")


@bot.message_handler(func=lambda m: m.text == "🎬 Сценарий Reels")
def smm_reels_handler(message):
    user_styles[message.from_user.id] = "smm_reels"
    waiting_for_smm.add(message.from_user.id)
    bot.send_message(message.chat.id, "🎬 Кидай тему, товар, услугу (или пришли фото):")


@bot.message_handler(func=lambda m: m.text == "📸 Идеи Сторис")
def smm_stories_handler(message):
    user_styles[message.from_user.id] = "smm_stories"
    waiting_for_smm.add(message.from_user.id)
    bot.send_message(message.chat.id, "📸 Кидай тему, товар, услугу (или пришли фото):")


@bot.message_handler(func=lambda m: m.text == "💡 Инфоповоды")
def smm_ideas_handler(message):
    user_styles[message.from_user.id] = "smm_ideas"
    waiting_for_smm.add(message.from_user.id)
    bot.send_message(message.chat.id, "💡 Кидай тему, товар, услугу (или пришли фото):")


@bot.message_handler(func=lambda m: m.from_user.id in waiting_for_smm)
def process_smm_text(message):
    if message.text == "◀️ Назад":
        waiting_for_smm.discard(message.from_user.id)
        bot.send_message(message.chat.id, "Главное меню:", reply_markup=get_main_keyboard())
        return

    style = user_styles.get(message.from_user.id)
    if not style:
        bot.reply_to(message, "⚠️ Сначала выбери SMM-инструмент.")
        return

    bot.reply_to(message, "⏳ Генерирую ответ...")

    try:
        prompt = PROMPTS[style] + f"\n\nТема пользователя: {message.text}\nСделай идеи конкретными, цепкими и готовыми к публикации."
        text = format_text(generate_text(prompt))
        send_long_message(message.chat.id, text)
        bot.send_message(message.chat.id, "Напиши новую тему или нажми «Назад»")
    except Exception as e:
        print(f"Ошибка SMM: {e}")
        bot.reply_to(message, "⚠️ Ошибка при генерации. Попробуй позже.")