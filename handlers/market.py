# handlers/market.py

from aiogram import Router, F, Bot
import json
from aiogram.types import Message, CallbackQuery, WebAppInfo, PreCheckoutQuery
from aiogram.exceptions import TelegramBadRequest

from keyboards.inline import (
    get_games_keyboard,
    get_items_keyboard,
    get_deal_details_keyboard,
    get_item_details_keyboard
)
from utils.db import (
    get_games,
    get_items_by_game,
    get_item_details,
    update_item_status, 
    get_user_balance,
    update_user_balance,
    get_user_profile
)
from config import WEB_APP_URL, SELLING_PRICE_COMMISSION

router = Router()

def get_deal_text(deal_info, current_user_id):
    """
    Формирует текст с деталями сделки.
    """
    status_map = {
        'in_progress': 'В процессе',
        'item_sent': 'Ожидает подтверждения от покупателя',
        'completed': 'Завершена',
        'cancelled': 'Отменена',
        'in_dispute': 'Открыт спор'
    }

    if current_user_id == deal_info['buyer_id']:
        role = "Покупатель"
        partner_username = deal_info.get('seller_username', 'Система')
    else:
        role = "Продавец"
        partner_username = deal_info.get('buyer_username', 'Неизвестно')

    server_info = f"🖥️ Сервер: {deal_info['server']}\n" if deal_info.get('server') else ""

    return (
        f"📋 Детали сделки #{deal_info['id']}\n\n"
        f"🔹 Товар: {deal_info['item_name']}\n"
        f"{server_info}"
        f"💰 Сумма: {deal_info['price']:.2f} RUB\n\n"
        f"👤 Ваша роль: {role}\n"
        f"👥 Ваш партнер: @{partner_username}\n\n"
        f"Статус: <b>{status_map.get(deal_info['status'], 'Неизвестен')}</b>"
    )


# --- CUSTOM FILTER ---
def is_purchase_data(message: Message) -> bool:
    """Проверяет, являются ли данные из Web App данными о покупке."""
    try:
        data = json.loads(message.web_app_data.data)
        # Проверяем наличие ключа type со значением purchase_item
        return data.get('type') == 'purchase_item' and 'itemId' in data
    except (json.JSONDecodeError, AttributeError):
        return False

# --- ОБРАБОТКА ДАННЫХ ИЗ WEB APP ---

@router.message(F.web_app_data, is_purchase_data)
async def process_purchase_web_app_data(message: Message, bot: Bot):
    """
    Этот хендлер обрабатывает подтверждение покупки из Web App.
    """
    try:
        data = json.loads(message.web_app_data.data)
        item_id = int(data['itemId'])
    except (json.JSONDecodeError, KeyError, ValueError):
        # Это сообщение видит пользователь в чате, если что-то пошло не так.
        await message.answer("❌ Произошла ошибка при обработке покупки. Попробуйте снова.")
        return

    # 1. Получаем детали товара
    item_details = get_item_details(item_id)
    if not item_details or item_details.get('status') != 'on_sale':
        # Сообщение на случай, если товар уже продан или снят с продажи
        await message.answer("❌ К сожалению, этот товар уже недоступен.")
        return

    buyer_id = message.from_user.id
    seller_id = item_details.get('seller_id')

    # 2. Проверяем, не покупает ли пользователь свой товар
    if seller_id and seller_id == buyer_id:
        await message.answer("🤔 Вы не можете купить свой собственный товар.")
        return

    # 3. Меняем статус товара на 'sold'
    update_item_status(item_id, 'sold')

    # 4. Отправляем уведомление продавцу, если он есть
    if seller_id:
        try:
            seller_message = (
                f"🎉 Ваш товар «<b>{item_details['name']}</b>» был успешно продан!\n\n"
                f"Покупатель: @{message.from_user.username}\n"
                f"Сумма: {item_details['price']:.2f} RUB\n\n"
                f"Скоро мы добавим функционал для автоматического перевода средств, а пока, пожалуйста, свяжитесь с покупателем для завершения сделки."
            )
            await bot.send_message(seller_id, seller_message, parse_mode="HTML")
        except TelegramBadRequest:
            print(f"Не удалось отправить уведомление продавцу {seller_id}. Возможно, он заблокировал бота.")

    # 5. Подтверждение для покупателя (отправляется в чат)
    # Это сообщение можно будет убрать, так как юзер уже видит success screen
    await bot.send_message(chat_id=message.from_user.id, text=f"✅ <b>Покупка успешна!</b>\n\nВы приобрели: {item_details['name']}\nЦена: {item_details['price']} ₽\n\nПродавец (@{item_details['seller_username']}) скоро свяжется с вами для передачи товара.", parse_mode="HTML")

# --- Логика для обработки запроса от web_server.py ---

async def process_purchase_from_web(bot: Bot, user_id: int, item_id: int) -> dict:
    """
    Обрабатывает покупку, инициированную через API.
    Возвращает словарь со статусом операции.
    """
    item_details = get_item_details(item_id)
    if not item_details or item_details['status'] != 'active':
        return {'status': 'error', 'message': 'Товар не найден или уже продан.'}

    seller_id = item_details['seller_id']
    if user_id == seller_id:
        return {'status': 'error', 'message': 'Вы не можете купить свой собственный товар.'}

    user_balance = get_user_balance(user_id)
    item_price = item_details['price']
    if user_balance < item_price:
        return {'status': 'error', 'message': f'Недостаточно средств. Ваш баланс: {user_balance} ₽'}

    # Проведение транзакции
    update_user_balance(user_id, -item_price) # Снимаем деньги у покупателя
    update_user_balance(seller_id, item_price) # Начисляем деньги продавцу
    update_item_status(item_id, 'sold') # Меняем статус товара

    # Уведомление покупателя
    await bot.send_message(
        chat_id=user_id, 
        text=f"✅ <b>Покупка успешна!</b>\n\nВы приобрели: {item_details['name']}\nЦена: {item_price} ₽\n\nПродавец (@{item_details['seller_username']}) скоро свяжется с вами для передачи товара.",
        parse_mode="HTML"
    )
    # Уведомление продавца
    await bot.send_message(
        chat_id=seller_id, 
        text=f"🔔 <b>Ваш товар купили!</b>\n\nТовар: {item_details['name']}\nЦена: {item_price} ₽\nПокупатель: @{get_user_profile(user_id)['username']}\n\nПожалуйста, свяжитесь с покупателем для передачи товара.",
        parse_mode="HTML"
    )

    return {'status': 'success', 'message': 'Покупка успешно совершена!'}


# --- РАЗДЕЛ ПОКУПКИ ---

@router.callback_query(F.data == "buy_menu")
async def buy_menu_handler(callback: CallbackQuery):
    games = get_games()
    await callback.message.edit_text("Выберите игру:", reply_markup=get_games_keyboard(games))


@router.callback_query(F.data.startswith("game_"))
async def game_handler(callback: CallbackQuery):
    game_id = int(callback.data.split("_")[1])
    page = 1
    items, total_items = get_items_by_game(game_id, page=page)

    if not items:
        await callback.answer("В этой категории пока нет товаров.", show_alert=True)
        return

    await callback.message.edit_text(
        "Выберите товар:",
        reply_markup=get_items_keyboard(items, game_id, page, total_items)
    )


@router.callback_query(F.data.startswith("items_page_"))
async def items_page_handler(callback: CallbackQuery):
    try:
        _, _, game_id_str, page_str = callback.data.split("_")
        game_id = int(game_id_str)
        page = int(page_str)
    except (ValueError, IndexError):
        await callback.answer("Ошибка данных пагинации.", show_alert=True)
        return

    items, total_items = get_items_by_game(game_id, page=page)

    if not items:
        await callback.answer("На этой странице нет товаров.", show_alert=True)
        return

    try:
        await callback.message.edit_text(
            "Выберите товар:",
            reply_markup=get_items_keyboard(items, game_id, page, total_items)
        )
    except TelegramBadRequest:
        await callback.answer() # Просто подтверждаем получение колбэка, чтобы убрать "часики"


@router.callback_query(F.data.startswith("item_"))
async def item_handler(callback: CallbackQuery):
    try:
        _, item_id_str, game_id_str, page_str = callback.data.split("_")
        item_id = int(item_id_str)
        game_id = int(game_id_str)
        page = int(page_str)
    except (ValueError, IndexError):
        await callback.answer("Ошибка данных товара.", show_alert=True)
        return

    item_details = get_item_details(item_id)

    if not item_details:
        await callback.answer("Товар не найден.", show_alert=True)
        return

    text = (
        f"<b>{item_details['name']}</b>\n\n"
        f"{item_details['description']}\n\n"
        f"<b>Цена:</b> {item_details['price']} RUB\n"
        f"<b>Продавец:</b> @{item_details['seller_username']}"
    )

    await callback.message.edit_text(
        text,
        reply_markup=get_item_details_keyboard(item_details, game_id, page, WEB_APP_URL),
        parse_mode="HTML"
    )
