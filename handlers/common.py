from datetime import datetime

from config import bot, FREE_LIMIT
from bot_ui.keyboards import (
    get_main_keyboard,
    get_back_keyboard,
    get_style_inline_keyboard,
    get_seo_keyboard,
)
from bot_ui.states import (
    user_styles,
    user_info,
    waiting_for_info,
    waiting_for_topic,
    waiting_for_link,
    waiting_for_smm,
    waiting_for_manager_chat,
    waiting_for_manager_question,
)
from storage.user_store import save_user, get_count, is_premium, load_users, get_premium_expiry


@bot.message_handler(commands=["start"])
def start(message):
    save_user(message.from_user)
    bot.reply_to(
        message,
        f"<b>Привет! Я помогу тебе создавать контент и продавать больше.</b>\n\n"
        f"📸 <b>Отправь фото товара</b> — напишу название и описание.\n"
        f"📋 <b>Свои хар-ки</b> — добавить характеристики вручную\n"
        f"🎨 <b>Стиль</b> — выбрать формат описания\n"
        f"📱 <b>Поиск по фото</b> — найду товар в интернете\n"
        f"🧠 <b>Помощник менеджера</b> — советы по работе с клиентами\n\n",
        parse_mode="HTML",
        reply_markup=get_main_keyboard()
    )

@bot.message_handler(commands=["id"])
def my_id(message):
    bot.reply_to(message, f"Твой ID: {message.from_user.id}")


@bot.message_handler(func=lambda m: m.from_user.id in waiting_for_info)
def save_info(message):
    if message.text == "◀️ Назад":
        waiting_for_info.discard(message.from_user.id)
        bot.send_message(message.chat.id, "Ввод отменён.", reply_markup=get_main_keyboard())
        return

    user_info[message.from_user.id] = message.text
    waiting_for_info.discard(message.from_user.id)
    bot.send_message(message.chat.id, "✅ Характеристики сохранены! Теперь отправь фото.", reply_markup=get_seo_keyboard())


@bot.message_handler(func=lambda m: m.text == "📋 Свои хар-ки")
def info_handler(message):
    waiting_for_info.add(message.from_user.id)
    bot.send_message(
        message.chat.id,
        "Отправь характеристики товара (каждая с новой строки). Например:\n\n"
        "<code>Размер: 60 см\nМатериал: металл\nЦвет: чёрный\nПатроны: E27 x 6</code>\n\n"
        "<b>Или нажми «Назад», если передумал вводить данные.</b>",
        parse_mode="HTML",
        reply_markup=get_back_keyboard()
    )


@bot.message_handler(func=lambda m: m.text == "🎨 Выбрать стиль")
def style_handler(message):
    bot.send_message(message.chat.id, "В каком формате писать текст?", reply_markup=get_style_inline_keyboard())


@bot.callback_query_handler(func=lambda call: call.data.startswith("set_style_"))
def callback_set_style(call):
    style_key = call.data.replace("set_style_", "")
    user_styles[call.from_user.id] = style_key
    names = {"short": "Кратко", "detailed": "Подробно", "marketplace": "Маркетплейс"}

    bot.answer_callback_query(call.id, f"Стиль {names[style_key]} выбран!")
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"✅ Стиль установлен: <b>{names[style_key]}</b>\n\nТеперь отправь фото товара.",
        parse_mode="HTML"
    )


@bot.message_handler(func=lambda m: m.text == "◀️ Назад")
def back_handler(message):
    uid = message.from_user.id
    waiting_for_info.discard(uid)
    waiting_for_topic.discard(uid)
    waiting_for_link.discard(uid)
    waiting_for_smm.discard(uid)
    waiting_for_manager_chat.discard(uid)
    waiting_for_manager_question.discard(uid)
    user_styles[uid] = "detailed"
    bot.send_message(message.chat.id, "Возврат в главное меню", reply_markup=get_main_keyboard())

@bot.message_handler(
    func=lambda message: (
        message.content_type == "text"
        and message.text not in {
            "🚀 SEO инструменты",
            "📱 SMM инструменты",
            "🧠 Помощник менеджера",
            "📋 Свои хар-ки",
            "🎨 Выбрать стиль",
            "📍 Собрать ключи",
            "🏷 Мета-теги (T/D)",
            "✌️ Рерайт по ссылке",
            "💰 Анализ цен",
            "📱 Пост по фото",
            "✌️ Пост по теме",
            "🎬 Сценарий Reels",
            "📸 Идеи Сторис",
            "💡 Инфоповоды",
            "💬 Отправить переписку",
            "❓ Задать вопрос менеджера",
            "❓ FAQ для сайта",
            "⚡ Быстрые скрипты",
            "◀️ Назад",
        }
        and message.from_user.id not in waiting_for_info
        and message.from_user.id not in waiting_for_topic
        and message.from_user.id not in waiting_for_link
        and message.from_user.id not in waiting_for_smm
        and message.from_user.id not in waiting_for_manager_chat
        and message.from_user.id not in waiting_for_manager_question
    )
)
def handle_unknown_text(message):
    bot.reply_to(message, "📸 Отправь фото товара, и я напишу описание.", reply_markup=get_main_keyboard())
