from datetime import datetime, timedelta

from config import bot, ADMIN_ID
from storage.user_store import load_users, save_users


@bot.message_handler(commands=["send"])
def send_broadcast(message):
    if message.from_user.id != ADMIN_ID:
        return

    text = message.text.replace("/send", "").strip()
    if not text:
        bot.reply_to(message, "Текст пустой. Используй: /send Текст сообщения")
        return

    users = load_users()
    success, fail = 0, 0

    for uid in users:
        try:
            bot.send_message(int(uid), text)
            success += 1
        except Exception:
            fail += 1

    bot.reply_to(message, f"✅ Отправлено: {success}\n❌ Ошибок: {fail}")


@bot.message_handler(commands=["users"])
def users_count(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, f"❌ Нет доступа.\nТвой ID: {message.from_user.id}\nADMIN_ID: {ADMIN_ID}")
        return

    users = load_users()
    bot.reply_to(message, f"👥 Всего пользователей: {len(users)}")



