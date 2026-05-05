from datetime import datetime
from html import escape

from config import bot, ADMIN_ID, TARGET_CHANNEL_ID
from bot_ui.keyboards import get_admin_draft_inline_keyboard
from parsers.telegram_parser import run_parser
from storage.post_queue import (
    get_draft,
    mark_posted,
    mark_skipped,
    schedule_post,
    get_scheduled_posts,
)
from scheduling.schedule_utils import find_next_free_slot


def _send_drafts_to_admin(chat_id, drafts):
    sent_count = 0

    for draft in drafts:
        try:
            photo_mark = "Да" if draft.get("has_photo") else "Нет"
            rewritten_text = draft.get("rewritten_text", "").strip() or "⚠️ Рерайт не получился. Проверь исходный пост вручную."

            text = (
                f"<b>Источник:</b> {escape(str(draft['channel']))}\n"
                f"<b>ID поста:</b> {draft['message_id']}\n"
                f"<b>Фото:</b> {photo_mark}\n\n"
                f"<b>Рерайт:</b>\n{escape(rewritten_text)}"
            )

            if len(text) > 4000:
                text = text[:4000] + "\n\n...[обрезано]"

            bot.send_message(
                chat_id,
                text,
                parse_mode="HTML",
                reply_markup=get_admin_draft_inline_keyboard(draft["post_key"])
            )
            sent_count += 1
        except Exception as e:
            print(f"[ADMIN SEND ERROR] {draft.get('channel')} / {draft.get('message_id')}: {e}")

    return sent_count


@bot.message_handler(commands=["parse_posts"])
def parse_posts_command(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Нет доступа.")
        return

    bot.reply_to(message, "⏳ Ищу новые посты в источниках...")

    try:
        drafts = run_parser()
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Ошибка парсера:\n{e}")
        return

    if not drafts:
        bot.send_message(message.chat.id, "Новых постов не найдено.")
        return

    sent_count = _send_drafts_to_admin(message.chat.id, drafts)
    bot.send_message(message.chat.id, f"✅ Черновиков отправлено: {sent_count}")


@bot.callback_query_handler(func=lambda call: call.data.startswith("publish::"))
def publish_post_callback(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "Нет доступа")
        return

    post_key = call.data.split("::", 1)[1]
    draft = get_draft(post_key)

    if not draft:
        bot.answer_callback_query(call.id, "Черновик не найден")
        return

    try:
        bot.send_message(TARGET_CHANNEL_ID, draft["rewritten_text"])
        mark_posted(post_key)
        bot.answer_callback_query(call.id, "Опубликовано")
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    except Exception as e:
        bot.answer_callback_query(call.id, "Ошибка публикации")
        bot.send_message(call.message.chat.id, f"⚠️ Ошибка публикации: {e}")


@bot.callback_query_handler(func=lambda call: call.data.startswith("schedule::"))
def schedule_post_callback(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "Нет доступа")
        return

    post_key = call.data.split("::", 1)[1]
    draft = get_draft(post_key)

    if not draft:
        bot.answer_callback_query(call.id, "Черновик не найден")
        return

    scheduled_posts = get_scheduled_posts()
    existing_slots = []

    for _, item in scheduled_posts:
        dt_str = item.get("scheduled_for")
        if dt_str:
            existing_slots.append(datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S"))

    next_slot = find_next_free_slot(existing_slots)

    if not next_slot:
        bot.answer_callback_query(call.id, "Нет свободного слота")
        return

    schedule_post(post_key, next_slot)

    bot.answer_callback_query(call.id, f"Запланировано: {next_slot.strftime('%d.%m %H:%M')}")
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    bot.send_message(
        call.message.chat.id,
        f"🕒 Пост запланирован на <b>{next_slot.strftime('%d.%m.%Y %H:%M')}</b>",
        parse_mode="HTML"
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("skip::"))
def skip_post_callback(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "Нет доступа")
        return

    post_key = call.data.split("::", 1)[1]
    mark_skipped(post_key)
    bot.answer_callback_query(call.id, "Пропущено")
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
