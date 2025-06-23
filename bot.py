# bot.py

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN
from handlers import start, market, sell, profile, admin, support
from web_server import web_server_task
from utils.db import init_db, populate_initial_data

async def main():
    # Инициализация базы данных
    init_db()
    populate_initial_data() # Заполняем БД играми и товарами

    # Инициализация бота и диспетчера
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # Подключение роутеров
    dp.include_router(start.router)
    dp.include_router(market.router)
    dp.include_router(profile.router)
    dp.include_router(sell.router)
    dp.include_router(admin.router)
    dp.include_router(support.router)
    # Другие роутеры будут здесь...

    # Создаем задачи для бота и веб-сервера
    bot_task = dp.start_polling(bot)
    server_task = web_server_task(bot)

    # Запускаем обе задачи одновременно
    logging.info("Запуск бота и веб-сервера...")
    await asyncio.gather(bot_task, server_task)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен.")
