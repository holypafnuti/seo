from config import bot

import handlers.manager  
import handlers.seo
import handlers.smm
import handlers.admin
import handlers.common


def main():
    print("Бот запущен!")
    bot.infinity_polling(skip_pending=True)


if __name__ == "__main__":
    main()