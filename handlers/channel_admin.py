from datetime import datetime
from html import escape
import re

from config import bot
from bot_ui.keyboards import get_channel_admin_keyboard
from bot_ui.states import waiting_for_schedule_input, waiting_for_channels_input
from storage.post_queue import load_queue
from storage.channel_admin_settings import (
    toggle_autoparsing,
    save_custom_slots,
    get_custom_slots,
    get_channels,
    save_channels,
)
from storage.user_store import is_premium
from handlers.admin_posts import parse_posts_command


def normalize_channel_name(raw: str):
    value = raw.strip()

    if value.startswith("https://t.me/"):
        value = value.replace("https://t.me/", "")
    elif value.startswith("http://t.me/"):
        value = value.replace("http://t.me/", "")

    if value.startswith("@"):
        value = value[1:]

    value = value.strip("/").strip()

    if not re.fullmatch(r"[A-Za-z0-9_]{4,32}", value):
        return None

    return value


@bot.message_handler(func=lambda m: m.text == "📣 Админам каналов")
def channel_admin_menu(message):
    bot.send_message(
        message.chat.id,
        "Раздел управления каналом:",
        reply_markup=get_channel_admin_keyboard()
    )


@bot.message_handler(func=lambda m: m.text in ["📡 Мои каналы", "➕ Добавить канал", "Добавить канал"])
def channels_handler(message):
    current_channels = get_channels()
    premium = is_premium(message.from_user.id)
    limit = 10 if premium else 1

    channels_text = "\n".join(current_channels) if current_channels else "Пока не добавлено ни одного канала."
    waiting_for_channels_input.add(message.from_user.id)

    bot.send_message(
        message.chat.id,
        f"Отправь username каналов списком, каждый с новой строки.\n\n"
        f"Можно в формате:\n"
        f"<code>@channel_name</code>\n"
        f"<code>channel_name</code>\n"
        f"<code>https://t.me/channel_name</code>\n\n"
        f"Чтобы выйти, нажми <b>◀️ Назад</b> или другую кнопку меню.\n\n"
        f"Текущие каналы:\n<code>{channels_text}</code>\n\n"
        f"Твой лимит: <b>{limit}</b> канал(ов).",
        parse_mode="HTML",
        reply_markup=get_channel_admin_keyboard()
    )


@bot.message_handler(func=lambda m: m.from_user.id in waiting_for_channels_input)
def save_channels_handler(message):
    admin_menu_buttons = {
        "📡 Мои каналы",
        "🕒 Пример расписания",
        "📝 Черновики",
        "📥 Получить посты",
        "🤖 Автопарсинг",
        "◀️ Назад",
        "📣 Админам каналов",
        "🚀 SEO инструменты",
        "📱 SMM инструменты",
        "👤 Мой статус",
    }

    if message.text in admin_menu_buttons:
        waiting_for_channels_input.discard(message.from_user.id)

        if message.text == "📥 Получить посты":
            parse_posts_command(message)
            return
        if message.text == "📝 Черновики":
            drafts_handler(message)
            return
        if message.text == "🕒 Пример расписания":
            schedule_example_handler(message)
            return
        if message.text == "🤖 Автопарсинг":
            autoparsing_toggle_handler(message)
            return
        if message.text == "📡 Мои каналы":
            channels_handler(message)
            return
        if message.text == "📣 Админам каналов":
            channel_admin_menu(message)
            return
        if message.text == "◀️ Назад":
            bot.send_message(message.chat.id, "Возврат в меню.", reply_markup=get_channel_admin_keyboard())
            return
        return

    raw_lines = [line.strip() for line in message.text.splitlines() if line.strip()]
    if not raw_lines:
        bot.reply_to(message, "❌ Ты ничего не отправил.", reply_markup=get_channel_admin_keyboard())
        return

    valid_channels = []
    invalid_lines = []

    for line in raw_lines:
        channel = normalize_channel_name(line)
        if channel:
            valid_channels.append(channel)
        else:
            invalid_lines.append(line)

    if invalid_lines:
        bad_text = "\n".join(invalid_lines[:10])
        bot.reply_to(
            message,
            "❌ Эти строки не похожи на username Telegram-каналов:\n\n"
            f"<code>{bad_text}</code>\n\n"
            "Отправь каналы в формате:\n"
            "<code>@channel_name</code>\n"
            "<code>channel_name</code>\n"
            "<code>https://t.me/channel_name</code>",
            parse_mode="HTML",
            reply_markup=get_channel_admin_keyboard()
        )
        return

    current_channels = get_channels()
    merged_channels = current_channels[:]
    for channel in valid_channels:
        if channel not in merged_channels:
            merged_channels.append(channel)

    premium = is_premium(message.from_user.id)
    limit = 10 if premium else 1

    if len(merged_channels) > limit:
        bot.reply_to(
            message,
            f"❌ Слишком много каналов.\n"
            f"Твой лимит: {limit}\n"
            f"Сейчас сохранено: {len(current_channels)}\n"
            f"После добавления будет: {len(merged_channels)}",
            reply_markup=get_channel_admin_keyboard()
        )
        return

    save_channels(merged_channels)
    waiting_for_channels_input.discard(message.from_user.id)

    saved_text = "\n".join(merged_channels) if merged_channels else "Список пуст."

    bot.reply_to(
        message,
        f"✅ Каналы сохранены.\n\nТекущий список:\n<code>{saved_text}</code>",
        parse_mode="HTML",
        reply_markup=get_channel_admin_keyboard()
    )


@bot.message_handler(func=lambda m: m.text == "🕒 Пример расписания")
def schedule_example_handler(message):
    waiting_for_schedule_input.add(message.from_user.id)

    current_slots = get_custom_slots()
    slots_text = "\n".join(current_slots)

    bot.send_message(
        message.chat.id,
        "Отправь свое расписание списком, каждое время с новой строки.\n\n"
        "Пример:\n"
        "<code>08:00\n11:15\n14:30\n17:45\n21:00</code>\n\n"
        f"Текущее расписание:\n<code>{slots_text}</code>\n\n"
        "После отправки оно станет расписанием по умолчанию.",
        parse_mode="HTML",
        reply_markup=get_channel_admin_keyboard()
    )


@bot.message_handler(func=lambda m: m.from_user.id in waiting_for_schedule_input)
def save_schedule_list_handler(message):
    if message.text == "◀️ Назад":
        waiting_for_schedule_input.discard(message.from_user.id)
        bot.send_message(message.chat.id, "Возврат в меню.", reply_markup=get_channel_admin_keyboard())
        return

    raw_lines = [line.strip() for line in message.text.splitlines() if line.strip()]
    valid_slots = []

    for line in raw_lines:
        try:
            datetime.strptime(line, "%H:%M")
            valid_slots.append(line)
        except ValueError:
            bot.reply_to(message, f"❌ Неверный формат времени: {line}\nИспользуй HH:MM, например 08:00")
            return

    if not valid_slots:
        bot.reply_to(message, "❌ Список пустой.")
        return

    valid_slots = sorted(valid_slots)
    save_custom_slots(valid_slots)
    waiting_for_schedule_input.discard(message.from_user.id)

    bot.reply_to(
        message,
        "✅ Новое расписание сохранено:\n\n" + "\n".join(valid_slots),
        reply_markup=get_channel_admin_keyboard()
    )


@bot.message_handler(func=lambda m: m.text == "📥 Получить посты")
def get_posts_handler(message):
    print("[BUTTON] Получить посты нажата")
    parse_posts_command(message)


@bot.message_handler(func=lambda m: m.text == "📝 Черновики")
def drafts_handler(message):
    queue = load_queue()
    drafts = [(k, v) for k, v in queue.items() if v.get("status") == "draft"]

    if not drafts:
        bot.reply_to(message, "Черновиков пока нет.", reply_markup=get_channel_admin_keyboard())
        return

    bot.send_message(message.chat.id, f"📝 Черновиков: {len(drafts)}")

    for post_key, item in drafts[:10]:
        text = item.get("rewritten_text", "").strip() or "⚠️ Пустой черновик"
        preview = text[:800]
        msg = (
            f"<b>{escape(post_key)}</b>\n"
            f"<b>Источник:</b> {escape(str(item.get('channel', '')))}\n"
            f"<b>Статус:</b> {escape(str(item.get('status', '')))}\n\n"
            f"{escape(preview)}"
        )
        bot.send_message(message.chat.id, msg, parse_mode="HTML")


@bot.message_handler(func=lambda m: m.text == "🤖 Автопарсинг")
def autoparsing_toggle_handler(message):
    enabled = toggle_autoparsing()
    status = "включен" if enabled else "выключен"

    bot.reply_to(
        message,
        f"🤖 Автопарсинг {status}.",
        reply_markup=get_channel_admin_keyboard()
    )
