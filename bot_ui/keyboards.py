from urllib.parse import quote
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def get_main_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("🚀 SEO инструменты"), KeyboardButton("📱 SMM инструменты"))
    kb.add(KeyboardButton("🧠 Помощник менеджера"))
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
    kb.add(KeyboardButton("❓ FAQ для сайта"), KeyboardButton("◀️ Назад"))
    return kb


def get_smm_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("📱 Пост по фото"), KeyboardButton("✌️ Пост по теме"))
    kb.add(KeyboardButton("🎬 Сценарий Reels"), KeyboardButton("📸 Идеи Сторис"))
    kb.add(KeyboardButton("💡 Инфоповоды"), KeyboardButton("◀️ Назад"))
    return kb


def get_manager_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("🔍 Найти похожие"), KeyboardButton("❓ Задай любой вопрос"))
    kb.add(KeyboardButton("⚡ Быстрые скрипты"), KeyboardButton("📚 Справочник"))
    kb.add(KeyboardButton("💬 Отправить переписку"), KeyboardButton("◀️ Назад"))
    return kb


def get_style_inline_keyboard():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("📝 Кратко", callback_data="set_style_short"))
    kb.add(InlineKeyboardButton("📄 Подробно", callback_data="set_style_detailed"))
    kb.add(InlineKeyboardButton("🛒 Маркетплейс", callback_data="set_style_marketplace"))
    return kb


def get_scripts_inline_keyboard():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("💰 Дорого, я подумаю", callback_data="script_expensive"),
        InlineKeyboardButton("🏪 Сравнивает с конкурентами", callback_data="script_competitors"),
        InlineKeyboardButton("🤐 Молчит после цены", callback_data="script_silence"),
        InlineKeyboardButton("🎁 Просит скидку", callback_data="script_discount"),
        InlineKeyboardButton("❓ Сомневается в качестве", callback_data="script_quality"),
        InlineKeyboardButton("📦 Товара нет в наличии", callback_data="script_nostock"),
    )
    return kb


def get_handbook_inline_keyboard():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("📞 Скрипт первого звонка", callback_data="hb_first_call"),
        InlineKeyboardButton("💳 Реквизиты для оплаты", callback_data="hb_payment"),
        InlineKeyboardButton("🚚 Доставка и оплата", callback_data="hb_delivery"),
        InlineKeyboardButton("🔍 Где искать товары", callback_data="hb_search"),
        InlineKeyboardButton("❓ Ответы на частые вопросы", callback_data="hb_faq"),
        InlineKeyboardButton("🔗 Полезные ссылки", callback_data="hb_links"),
    )
    return kb


def get_search_lens_keyboard(file_url: str, query: str):
    """Кнопки поиска похожих товаров по фото и названию"""
    lens_url = f"https://lens.google.com/uploadbyurl?url={quote(file_url, safe='')}&q={quote('купить Донплафон Империум 33 идеи', safe='')}"
    ya_lens = f"https://yandex.ru/images/search?rpt=imageview&url={quote(file_url, safe='')}"
    q = quote(query, safe="")
    q_buy = quote(f"купить {query}", safe="")

    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("🌐 Google — поиск по фото", url=lens_url),
        InlineKeyboardButton("🌐 Яндекс — поиск по фото", url=ya_lens),
        InlineKeyboardButton("🔎 Google — поиск по названию", url=f"https://www.google.com/search?q={quote(f'купить {query} Донплафон Империум 33идеи', safe='')}"),
    )
    return kb
