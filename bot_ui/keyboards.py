from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def get_main_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("🚀 SEO инструменты"), KeyboardButton("📱 SMM инструменты"))
    kb.add(KeyboardButton("🧠 Помощник менеджера"))
    kb.add(KeyboardButton("👤 Мой статус"))
    return kb


def get_back_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("◀️ Назад"))
    return kb


def get_seo_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("🎨 Выбрать стиль"), KeyboardButton("📋 Свои хар-ки"))
    kb.add(KeyboardButton("📍 Собрать ключи"), KeyboardButton("🏷 Мета-теги (T/D)"))
    kb.add(KeyboardButton("✌️ Рерайт по ссылке"), KeyboardButton("💰 Анализ цен"))
    kb.add(KeyboardButton("◀️ Назад"))
    return kb


def get_smm_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("📱 Пост по фото"), KeyboardButton("✌️ Пост по теме"))
    kb.add(KeyboardButton("🎬 Сценарий Reels"), KeyboardButton("📸 Идеи Сторис"))
    kb.add(KeyboardButton("💡 Инфоповоды"), KeyboardButton("◀️ Назад"))
    return kb


def get_manager_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("💬 Отправить переписку"))
    kb.add(KeyboardButton("❓ Задать вопрос менеджера"))
    kb.add(KeyboardButton("◀️ Назад"))
    return kb
    
def get_seo_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("🎨 Выбрать стиль"), KeyboardButton("📋 Свои хар-ки"))
    kb.add(KeyboardButton("📍 Собрать ключи"), KeyboardButton("🏷 Мета-теги (T/D)"))
    kb.add(KeyboardButton("✌️ Рерайт по ссылке"), KeyboardButton("💰 Анализ цен"))
    kb.add(KeyboardButton("❓ FAQ для сайта"))  # ← новая кнопка
    kb.add(KeyboardButton("◀️ Назад"))
    return kb

def get_style_inline_keyboard():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("📝 Кратко", callback_data="set_style_short"))
    kb.add(InlineKeyboardButton("📄 Подробно", callback_data="set_style_detailed"))
    kb.add(InlineKeyboardButton("🛒 Маркетплейс", callback_data="set_style_marketplace"))
    return kb


def get_translate_inline_keyboard():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🇺🇸 Перевести на English", callback_data="translate_en"))
    return kb
