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


@bot.message_handler(commands=["premium"])
def give_premium(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, f"❌ Нет доступа.\nТвой ID: {message.from_user.id}\nADMIN_ID: {ADMIN_ID}")
        return

    parts = message.text.split()
    if len(parts) < 3:
        bot.reply_to(
            message,
            "Используй: <code>/premium ID ДНИ</code>\nПример: <code>/premium 12345 30</code>",
            parse_mode="HTML"
        )
        return

    target_uid = parts[1]

    try:
        days = int(parts[2])
    except ValueError:
        bot.reply_to(message, "❌ Дни должны быть числом.")
        return

    users = load_users()
    expiry_date = datetime.now() + timedelta(days=days)
    expiry_str = expiry_date.strftime("%Y-%m-%d")

    if target_uid not in users:
        users[target_uid] = {
            "id": int(target_uid),
            "username": "unknown",
            "count": 0
        }

    users[target_uid]["premium"] = True
    users[target_uid]["premium_until"] = expiry_str
    save_users(users)

    bot.reply_to(
        message,
        f"✅ Премиум выдан пользователю <code>{target_uid}</code> на {days} дней, до <b>{expiry_str}</b>",
        parse_mode="HTML"
    )

    try:
        bot.send_message(
            int(target_uid),
            f"🎉 Вам активирован <b>Премиум</b> на {days} дней.\n📅 До: <b>{expiry_str}</b>",
            parse_mode="HTML"
        )
    except Exception:
        pass


@bot.message_handler(commands=["check_expired"])
def check_expired_subscriptions(message):
    if message.from_user.id != ADMIN_ID:
        return

    users = load_users()
    today = datetime.now()
    reminded = 0

    for uid, data in users.items():
        if data.get("premium_until"):
            expiry = datetime.strptime(data["premium_until"], "%Y-%m-%d")
            days_left = (expiry - today).days

            if 0 < days_left <= 3:
                try:
                    bot.send_message(int(uid), f"⚠️ Внимание! Ваша подписка истекает через {days_left} дн. Не забудьте продлить!")
                    reminded += 1
                except Exception:
                    pass
            elif days_left < 0 and data.get("premium"):
                data["premium"] = False
                try:
                    bot.send_message(int(uid), "❌ Срок действия вашего Премиума истек. Вы вернулись на бесплатный лимит.")
                except Exception:
                    pass

    save_users(users)
    bot.reply_to(message, f"Проверка завершена. Отправлено {reminded} напоминаний.")
