import requests

from config import bot, TELEGRAM_TOKEN
from prompts import PROMPTS
from scripts import SCRIPTS
from bot_ui.states import waiting_for_manager_chat, waiting_for_manager_question
from bot_ui.keyboards import get_manager_keyboard, get_main_keyboard, get_scripts_inline_keyboard
from storage.user_store import check_limit, increment_count
from utils.formatting import format_text, send_long_message
from ai.router import generate_text, generate_multimodal


@bot.message_handler(func=lambda m: m.text == "🧠 Помощник менеджера")
def manager_menu(message):
    bot.send_message(
        message.chat.id,
        "🧠 <b>Помощник менеджера</b>\n\n"
        "Выбери режим:",
        parse_mode="HTML",
        reply_markup=get_manager_keyboard()
    )


@bot.message_handler(func=lambda m: m.text == "⚡ Быстрые скрипты")
def quick_scripts_handler(message):
    bot.send_message(
        message.chat.id,
        "⚡ <b>Быстрые скрипты</b>\n\nВыбери ситуацию — получишь готовый скрипт ответа:",
        parse_mode="HTML",
        reply_markup=get_scripts_inline_keyboard()
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("script_"))
def handle_script_callback(call):
    script = SCRIPTS.get(call.data)
    if not script:
        bot.answer_callback_query(call.id, "Скрипт не найден")
        return

    bot.answer_callback_query(call.id)
    bot.send_message(
        call.message.chat.id,
        format_text(script),
        parse_mode="HTML",
        reply_markup=get_manager_keyboard()
    )


@bot.message_handler(func=lambda m: m.text == "💬 Отправить переписку")
def manager_chat_handler(message):
    waiting_for_manager_chat.add(message.from_user.id)
    bot.send_message(
        message.chat.id,
        "💬 Отправь переписку с клиентом.\n\n"
        "Можно скопировать текстом или прислать <b>скриншот</b> — разберу в любом формате.",
        parse_mode="HTML",
        reply_markup=get_manager_keyboard()
    )


@bot.message_handler(func=lambda m: m.text == "❓ Задать вопрос менеджера")
def manager_question_handler(message):
    waiting_for_manager_question.add(message.from_user.id)
    bot.send_message(
        message.chat.id,
        "❓ Задай свой вопрос.\n\n"
        "Например:\n"
        "— Клиент говорит что дорого, как ответить?\n"
        "— Как убедить взять люстру побольше?\n"
        "— Клиент молчит после цены, что делать?",
        reply_markup=get_manager_keyboard()
    )


@bot.message_handler(func=lambda m: m.from_user.id in waiting_for_manager_chat)
def process_manager_chat(message):
    if message.text in ["◀️ Назад", "🧠 Помощник менеджера", "💬 Отправить переписку", "❓ Задать вопрос менеджера", "⚡ Быстрые скрипты"]:
        waiting_for_manager_chat.discard(message.from_user.id)
        if message.text == "◀️ Назад":
            bot.send_message(message.chat.id, "Главное меню", reply_markup=get_main_keyboard())
        elif message.text == "🧠 Помощник менеджера":
            manager_menu(message)
        elif message.text == "❓ Задать вопрос менеджера":
            manager_question_handler(message)
        elif message.text == "⚡ Быстрые скрипты":
            quick_scripts_handler(message)
        return

    if not check_limit(message):
        return

    increment_count(message.from_user.id)
    bot.reply_to(message, "⏳ Анализирую переписку...")

    try:
        prompt = PROMPTS["manager_help"] + "\n\nПЕРЕПИСКА:\n" + (message.text or "")
        result = generate_text(prompt)
        text = format_text(result)
        send_long_message(message.chat.id, text, reply_to=message)
        bot.send_message(
            message.chat.id,
            "Можешь отправить новую переписку или задать вопрос 👇",
            reply_markup=get_manager_keyboard()
        )
    except Exception as e:
        print(f"ОШИБКА manager_chat: {e}")
        bot.reply_to(message, "⚠️ Ошибка при анализе. Попробуй позже.")
    finally:
        waiting_for_manager_chat.discard(message.from_user.id)


@bot.message_handler(content_types=["photo"], func=lambda m: m.from_user.id in waiting_for_manager_chat)
def process_manager_chat_photo(message):
    if not check_limit(message):
        return

    increment_count(message.from_user.id)
    bot.reply_to(message, "⏳ Читаю скриншот переписки...")

    try:
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_info.file_path}"
        img_content = requests.get(file_url, timeout=30).content

        prompt = (
            PROMPTS["manager_help"]
            + "\n\nПЕРЕПИСКА (скриншот): прочитай текст с изображения и разбери переписку."
            + "\nВАЖНО: сообщения СПРАВА — менеджер (наша сторона), сообщения СЛЕВА — клиент."
        )
        result = generate_multimodal(prompt, img_content)
        text = format_text(result)
        send_long_message(message.chat.id, text, reply_to=message)
        bot.send_message(
            message.chat.id,
            "Можешь отправить новую переписку или задать вопрос 👇",
            reply_markup=get_manager_keyboard()
        )
    except Exception as e:
        print(f"ОШИБКА manager_chat_photo: {e}")
        bot.reply_to(message, "⚠️ Ошибка при обработке скриншота. Попробуй позже.")
    finally:
        waiting_for_manager_chat.discard(message.from_user.id)


@bot.message_handler(func=lambda m: m.from_user.id in waiting_for_manager_question)
def process_manager_question(message):
    if message.text in ["◀️ Назад", "🧠 Помощник менеджера", "💬 Отправить переписку", "❓ Задать вопрос менеджера", "⚡ Быстрые скрипты"]:
        waiting_for_manager_question.discard(message.from_user.id)
        if message.text == "◀️ Назад":
            bot.send_message(message.chat.id, "Главное меню", reply_markup=get_main_keyboard())
        elif message.text == "🧠 Помощник менеджера":
            manager_menu(message)
        elif message.text == "💬 Отправить переписку":
            manager_chat_handler(message)
        elif message.text == "⚡ Быстрые скрипты":
            quick_scripts_handler(message)
        return

    if not check_limit(message):
        return

    increment_count(message.from_user.id)
    bot.reply_to(message, "⏳ Думаю...")

    try:
        prompt = (
            PROMPTS["manager_help"]
            + f"\n\nВОПРОС МЕНЕДЖЕРА:\n{message.text}"
        )
        result = generate_text(prompt)
        text = format_text(result)
        send_long_message(message.chat.id, text, reply_to=message)
        bot.send_message(
            message.chat.id,
            "Можешь задать следующий вопрос или отправить переписку 👇",
            reply_markup=get_manager_keyboard()
        )
    except Exception as e:
        print(f"ОШИБКА manager_question: {e}")
        bot.reply_to(message, "⚠️ Ошибка при генерации. Попробуй позже.")
    finally:
        waiting_for_manager_question.discard(message.from_user.id)
