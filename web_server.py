import asyncio
import json
import logging
import os
from aiohttp import web
import aiohttp_cors
from aiogram import Bot
from aiogram.utils.web_app import safe_parse_webapp_init_data
from aiogram.exceptions import AiogramError

# Эти функции мы создадим в следующих шагах
from handlers.market import process_purchase_from_web
from handlers.sell import process_sell_from_web

# --- Безопасная проверка данных от Telegram ---
def check_auth_data(bot_token: str, init_data: str):
    try:
        # Этот метод проверяет подпись и срок действия данных.
        # Если проверка не пройдена, он вызовет исключение.
        return safe_parse_webapp_init_data(token=bot_token, init_data=init_data)
    except (ValueError, AiogramError) as e:
        logging.error(f"Ошибка валидации данных WebApp: {e}")
        return None

# --- Обработчики API ---
async def handle_purchase(request: web.Request):
    bot = request.app['bot']
    try:
        data = await request.json()
        init_data = data.get('initData')
        item_id = data.get('itemId')

        if not init_data or not item_id:
            return web.json_response({'status': 'error', 'message': 'Отсутствуют необходимые данные'}, status=400)

        auth_data = check_auth_data(bot.token, init_data)
        if not auth_data:
            return web.json_response({'status': 'error', 'message': 'Ошибка аутентификации'}, status=403)

        user_id = auth_data.user.id
        result = await process_purchase_from_web(bot, user_id, item_id)

        if result['status'] == 'success':
            return web.json_response({'status': 'ok', 'message': result['message']})
        else:
            return web.json_response({'status': 'error', 'message': result['message']}, status=400)

    except Exception as e:
        logging.exception("Критическая ошибка в handle_purchase")
        return web.json_response({'status': 'error', 'message': 'Внутренняя ошибка сервера'}, status=500)

async def handle_sell(request: web.Request):
    bot = request.app['bot']
    try:
        data = await request.json()
        init_data = data.get('initData')
        item_data = data.get('itemData')

        if not init_data or not item_data:
            return web.json_response({'status': 'error', 'message': 'Отсутствуют необходимые данные'}, status=400)

        auth_data = check_auth_data(bot.token, init_data)
        if not auth_data:
            return web.json_response({'status': 'error', 'message': 'Ошибка аутентификации'}, status=403)

        user_id = auth_data.user.id
        result = await process_sell_from_web(bot, user_id, item_data)

        if result['status'] == 'success':
            return web.json_response({'status': 'ok', 'message': result['message']})
        else:
            return web.json_response({'status': 'error', 'message': result['message']}, status=400)

    except Exception as e:
        logging.exception("Критическая ошибка в handle_sell")
        return web.json_response({'status': 'error', 'message': 'Внутренняя ошибка сервера'}, status=500)

# --- Запуск сервера ---
async def web_server_task(bot: Bot):
    app = web.Application()
    app['bot'] = bot

    cors = aiohttp_cors.setup(app, defaults={
        "https://diavora.github.io": aiohttp_cors.ResourceOptions(
            allow_credentials=True, expose_headers="*", allow_headers="*", allow_methods="*",
        ),
        # Для локального тестирования, открывая файл index.html напрямую
        "null": aiohttp_cors.ResourceOptions(allow_credentials=True, expose_headers="*", allow_headers="*", allow_methods="*")
    })

    app.router.add_post('/api/purchase', handle_purchase)
    app.router.add_post('/api/sell', handle_sell)

    for route in list(app.router.routes()):
        cors.add(route)

    runner = web.AppRunner(app)
    await runner.setup()
    
    # Amvera использует переменную PORT, если она есть, иначе 8000
    port = int(os.environ.get('PORT', 8000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logging.info(f"Веб-сервер запущен на http://0.0.0.0:{port}")

    # Бесконечное ожидание, чтобы задача не завершилась
    await asyncio.Event().wait()
