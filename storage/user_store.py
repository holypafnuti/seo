from datetime import datetime

from config import USERS_FILE, FREE_LIMIT, bot
from storage.json_store import load_json, save_json


def load_users():
    return load_json(USERS_FILE, {})


def save_users(users):
    save_json(USERS_FILE, users)


def save_user(user):
    users = load_users()
    uid = str(user.id)
    if uid not in users:
        users[uid] = {
            "id": user.id,
            "username": user.username or "",
            "first_name": user.first_name or "",
            "last_name": user.last_name or "",
            "count": 0,
            "premium": False
        }
        save_users(users)


def get_count(user_id):
    users = load_users()
    return users.get(str(user_id), {}).get("count", 0)


def increment_count(user_id):
    users = load_users()
    uid = str(user_id)
    if uid not in users:
        users[uid] = {"count": 0, "premium": False}
    users[uid]["count"] = users[uid].get("count", 0) + 1
    save_users(users)


def get_premium_expiry(user_id):
    users = load_users()
    expiry_str = users.get(str(user_id), {}).get("premium_until")
    if expiry_str:
        try:
            return datetime.strptime(expiry_str, "%Y-%m-%d")
        except Exception:
            return None
    return None


def is_premium(user_id):
    expiry_date = get_premium_expiry(user_id)
    if expiry_date:
        return datetime.now() <= expiry_date
    users = load_users()
    return users.get(str(user_id), {}).get("premium", False)


def check_limit(message):
    if is_premium(message.from_user.id):
        return True

    if get_count(message.from_user.id) >= FREE_LIMIT:
        bot.reply_to(
            message,
            f"❌ Бесплатный лимит {FREE_LIMIT} генераций исчерпан.\n\n"
            "Для получения Премиума напишите @holy_pafnuti"
        )
        return False
    return True
