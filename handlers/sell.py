import json
import logging
from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message, WebAppInfo

from keyboards.inline import (
    get_sell_games_keyboard,
    get_sell_servers_keyboard,
    get_open_sell_form_keyboard
)
from utils.db import get_games, add_item
from utils.games_data import GAMES_DATA
from config import WEB_APP_URL

router = Router()

class SellItem(StatesGroup):
    choosing_game = State()
    choosing_server = State()

# --- Хелпер для проверки, что данные пришли из формы продажи ---
def is_create_item_data(message: Message) -> bool:
    if not message.web_app_data:
        return False
    try:
        data = json.loads(message.web_app_data.data)
        # Проверяем наличие ключей, специфичных для формы продажи
        return all(k in data for k in ['gameId', 'name', 'description', 'price'])
    except (json.JSONDecodeError, AttributeError, TypeError):
        return False

# --- Обработчик данных из WebApp (когда юзер отправляет форму) ---
@router.message(F.web_app_data, is_create_item_data)
async def process_sell_web_app_data(message: Message, bot: Bot):
    try:
        item_data = json.loads(message.web_app_data.data)
        user_id = message.from_user.id

        # Вызываем новую централизованную функцию, которая также используется API
        result = await process_sell_from_web(bot, user_id, item_data)

        # Если функция вернула ошибку, сообщаем пользователю
        if result['status'] == 'error':
            await message.answer(f"❌ Ошибка: {result['message']}")

    except (json.JSONDecodeError, TypeError) as e:
        logging.error(f"Ошибка обработки данных из WebApp (sell): {e}")
        await message.answer("❌ Произошла ошибка при обработке ваших данных. Попробуйте снова.")

# --- Логика для обработки запроса от web_server.py (и от WebApp выше) ---
async def process_sell_from_web(bot: Bot, user_id: int, item_data: dict) -> dict:
    """
    Обрабатывает выставление товара на продажу.
    Используется и API, и прямыми данными из WebApp.
    """
    try:
        game_id = item_data['gameId']
        server = item_data.get('server')
        name = str(item_data['name']).strip()
        description = str(item_data['description']).strip()
        price = float(item_data['price'])

        # Валидация
        if not name or not description or price <= 0 or len(name) > 100 or len(description) > 500:
            return {'status': 'error', 'message': 'Некорректные данные товара. Проверьте длину полей и цену.'}
        
        # Добавление в БД
        add_item(seller_id=user_id, game_id=game_id, name=name, description=description, price=price, server=server)

        # Уведомление в ТГ
        await bot.send_message(
            chat_id=user_id, 
            text=f"✅ <b>Товар успешно выставлен на продажу!</b>\n\nНазвание: {name}\nЦена: {price} ₽",
            parse_mode="HTML"
        )
        return {'status': 'success', 'message': 'Товар успешно выставлен.'}

    except (KeyError, ValueError, TypeError) as e:
        logging.error(f"Ошибка обработки данных о товаре: {e} | Data: {item_data}")
        return {'status': 'error', 'message': 'Неполные или неверные данные о товаре.'}
    except Exception as e:
        logging.exception("Критическая ошибка в process_sell_from_web")
        return {'status': 'error', 'message': 'Внутренняя ошибка сервера.'}

# --- РАЗДЕЛ ПРОДАЖИ (навигация по кнопкам в боте) ---
@router.callback_query(F.data == "sell_item")
async def sell_item_handler(callback: CallbackQuery, state: FSMContext):
    games = get_games()
    await callback.message.edit_text(
        "Выберите игру, для которой хотите продать товар:",
        reply_markup=get_sell_games_keyboard(games)
    )
    await state.set_state(SellItem.choosing_game)

@router.callback_query(F.data.startswith("sell_game_"), SellItem.choosing_game)
async def choose_game_handler(callback: CallbackQuery, state: FSMContext):
    game_id = int(callback.data.split("_")[2])
    game_info = GAMES_DATA.get(game_id)

    if not game_info:
        await callback.answer("Игра не найдена!", show_alert=True)
        return

    await state.update_data(game_id=game_id, game_name=game_info['name'])

    if game_info.get('servers'):
        await callback.message.edit_text(
            f"Выбрана игра: <b>{game_info['name']}</b>.\nТеперь выберите сервер:",
            reply_markup=get_sell_servers_keyboard(game_id, game_info['servers'])
        )
        await state.set_state(SellItem.choosing_server)
    else:
        # Если у игры нет серверов, сразу открываем Web App
        url = f"{WEB_APP_URL}sell.html?gameId={game_id}&gameName={game_info['name']}"
        await callback.message.edit_text(
            f"Выбрана игра: <b>{game_info['name']}</b>.\n\nНажмите кнопку ниже, чтобы заполнить информацию о товаре.",
            reply_markup=get_open_sell_form_keyboard(url)
        )
        await state.clear()

@router.callback_query(F.data.startswith("sell_server_"), SellItem.choosing_server)
async def choose_server_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    game_id = data.get('game_id')
    game_name = data.get('game_name')
    server = callback.data.split("_")[2]

    url = f"{WEB_APP_URL}sell.html?gameId={game_id}&gameName={game_name}&server={server}"

    await callback.message.edit_text(
        f"Выбрана игра: <b>{game_name}</b>, сервер: <b>{server}</b>.\n\nНажмите кнопку ниже, чтобы заполнить информацию о товаре.",
        reply_markup=get_open_sell_form_keyboard(url)
    )
    await state.clear()


@router.callback_query(F.data == "back_to_games_list", SellItem.choosing_server)
async def back_to_games_list_handler(callback: CallbackQuery, state: FSMContext):
    await sell_item_handler(callback, state)

import json
import logging
from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message, WebAppInfo

from keyboards.inline import (
    get_sell_games_keyboard,
    get_sell_servers_keyboard,
    get_open_sell_form_keyboard
)
from utils.db import get_games, add_item
from utils.games_data import GAMES_DATA
from config import WEB_APP_URL

router = Router()

class SellItem(StatesGroup):
    choosing_game = State()
    choosing_server = State()

# --- Хелпер для проверки, что данные пришли из формы продажи ---
def is_create_item_data(message: Message) -> bool:
    if not message.web_app_data:
        return False
    try:
        data = json.loads(message.web_app_data.data)
        # Проверяем наличие ключей, специфичных для формы продажи
        return all(k in data for k in ['gameId', 'name', 'description', 'price'])
    except (json.JSONDecodeError, AttributeError, TypeError):
        return False

# --- Обработчик данных из старого WebApp (если он еще используется) ---
@router.message(F.web_app_data, is_create_item_data)
async def process_sell_web_app_data(message: Message, bot: Bot):
    try:
        item_data = json.loads(message.web_app_data.data)
        user_id = message.from_user.id

        # Вызываем новую централизованную функцию
        result = await process_sell_from_web(bot, user_id, item_data)

        if result['status'] == 'error':
            await message.answer(f"❌ Ошибка: {result['message']}")

    except (json.JSONDecodeError, TypeError) as e:
        logging.error(f"Ошибка обработки данных из WebApp (sell): {e}")
        await message.answer("❌ Произошла ошибка при обработке ваших данных. Попробуйте снова.")

# --- Логика для обработки запроса от web_server.py ---
async def process_sell_from_web(bot: Bot, user_id: int, item_data: dict) -> dict:
    """
    Обрабатывает выставление товара на продажу через API.
    """
    try:
        game_id = item_data['gameId']
        server = item_data.get('server')
        name = str(item_data['name']).strip()
        description = str(item_data['description']).strip()
        price = float(item_data['price'])

        if not name or not description or price <= 0 or len(name) > 100 or len(description) > 500:
            return {'status': 'error', 'message': 'Некорректные данные товара. Проверьте длину полей и цену.'}
        
        add_item(seller_id=user_id, game_id=game_id, name=name, description=description, price=price, server=server)

        await bot.send_message(
            chat_id=user_id, 
            text=f"✅ <b>Товар успешно выставлен на продажу!</b>\n\nНазвание: {name}\nЦена: {price} ₽",
            parse_mode="HTML"
        )
        return {'status': 'success', 'message': 'Товар успешно выставлен.'}

    except (KeyError, ValueError, TypeError) as e:
        logging.error(f"Ошибка обработки данных о товаре: {e}")
        return {'status': 'error', 'message': 'Неполные или неверные данные о товаре.'}
    except Exception as e:
        logging.exception("Критическая ошибка в process_sell_from_web")
        return {'status': 'error', 'message': 'Внутренняя ошибка сервера.'}

# --- РАЗДЕЛ ПРОДАЖИ (навигация по кнопкам в боте) ---
@router.callback_query(F.data == "sell_item")
async def sell_item_handler(callback: CallbackQuery, state: FSMContext):
    games = get_games()
    await callback.message.edit_text(
        "Выберите игру, для которой хотите продать товар:",
        reply_markup=get_sell_games_keyboard(games)
    )
    await state.set_state(SellItem.choosing_game)

@router.callback_query(F.data.startswith("sell_game_"), SellItem.choosing_game)
async def choose_game_handler(callback: CallbackQuery, state: FSMContext):
    game_id = int(callback.data.split("_")[2])
    game_info = GAMES_DATA.get(game_id)

    if not game_info:
        await callback.answer("Игра не найдена!", show_alert=True)
        return

    await state.update_data(game_id=game_id, game_name=game_info['name'])

    if game_info.get('servers'):
        await callback.message.edit_text(
            f"Выбрана игра: <b>{game_info['name']}</b>.\nТеперь выберите сервер:",
            reply_markup=get_sell_servers_keyboard(game_id, game_info['servers'])
        )
        await state.set_state(SellItem.choosing_server)
    else:
        url = f"{WEB_APP_URL}sell.html?gameId={game_id}&gameName={game_info['name']}"
        await callback.message.edit_text(
            f"Выбрана игра: <b>{game_info['name']}</b>.\n\nНажмите кнопку ниже, чтобы заполнить информацию о товаре.",
            reply_markup=get_open_sell_form_keyboard(url)
        )
        await state.clear()

@router.callback_query(SellItem.choosing_server, F.data.startswith("sell_server_page_"))
async def server_page_changed(callback: CallbackQuery, state: FSMContext):
    """Обрабатывает переключение страниц серверов."""
    page = int(callback.data.split("_")[3])
    data = await state.get_data()
    servers = data.get("servers", [])
    
    await callback.message.edit_text(
        f"<b>Игра:</b> {data['game_name']}\n\nВыберите сервер:",
        reply_markup=get_server_keyboard(servers, page=page),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(SellItem.choosing_server, F.data.startswith("sell_server_"))
async def server_chosen_for_sell(callback: CallbackQuery, state: FSMContext):
    """Обрабатывает выбор сервера и открывает Web App."""
    server_name = callback.data[len("sell_server_"):]
    data = await state.get_data()
    game_id = data['game_id']
    game_name = data['game_name']

    await callback.message.edit_text(
        f"<b>Игра:</b> {game_name}\n"
        f"<b>Сервер:</b> {server_name}\n\n"
        "Отлично! Теперь, пожалуйста, заполните детали вашего товара в веб-форме.",
        reply_markup=get_open_sell_webapp_keyboard(game_id, game_name, server_name, WEB_APP_URL),
        parse_mode="HTML"
    )
    await state.clear()
