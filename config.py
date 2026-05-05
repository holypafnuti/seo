import os
from pathlib import Path

import google.genai as genai
import telebot
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

load_dotenv(BASE_DIR / ".env")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")

ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
FREE_LIMIT = int(os.getenv("FREE_LIMIT", "100"))

bot = telebot.TeleBot(TELEGRAM_TOKEN) if TELEGRAM_TOKEN else telebot.TeleBot("000000:TEST")
gemini_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

USERS_FILE = DATA_DIR / "users.json"