from config import bot


def format_text(text: str) -> str:
    if not text:
        return ""
    result = ""
    parts = text.split("**")
    for i, part in enumerate(parts):
        if i % 2 == 1:
            result += f"<b>{part}</b>"
        else:
            result += part
    result = result.replace("*", "").replace("###", "").replace("##", "").replace("$", "")
    return result


def send_long_message(chat_id, text, reply_to=None):
    text = text or ""
    if len(text) > 4000:
        parts = [text[i:i + 4000] for i in range(0, len(text), 4000)]
        for part in parts:
            if reply_to:
                bot.reply_to(reply_to, part, parse_mode="HTML")
                reply_to = None
            else:
                bot.send_message(chat_id, part, parse_mode="HTML")
    else:
        if reply_to:
            bot.reply_to(reply_to, text, parse_mode="HTML")
        else:
            bot.send_message(chat_id, text, parse_mode="HTML")
