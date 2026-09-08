import asyncio
import os
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from handlers import router
from database import init_db

# Загружаем настройки, но если файла .env нет (на сервере), 
# то берет из переменных окружения
load_dotenv()

async def main():
    # Создаем базу данных, если ее еще нет
    init_db()
    
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    dp = Dispatcher()
    
    dp.include_router(router)
    
    print("ЕГЭ Бот успешно запущен!")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
