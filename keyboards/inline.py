# keyboards/inline.py

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from urllib.parse import quote_plus

# --- КЛАВИАТУРЫ АДМИН-ПАНЕЛИ ---

def get_disputes_list_keyboard(disputes):
    builder = InlineKeyboardBuilder()
    for dispute in disputes:
        builder.button(
            text=f"Спор #{dispute['id']} - {dispute['item_name']}", 
            callback_data=f"admin_dispute_{dispute['id']}"
        )
    builder.button(text="⬅️ Назад в админ-меню", callback_data="admin_menu")
    builder.adjust(1)
    return builder.as_markup()

def get_dispute_resolution_keyboard(deal_id, buyer_id, seller_id):
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ В пользу покупателя", callback_data=f"resolve_{deal_id}_to_{buyer_id}")
    builder.button(text="☑️ В пользу продавца", callback_data=f"resolve_{deal_id}_to_{seller_id}")
    builder.button(text="⬅️ К списку споров", callback_data="manage_disputes")
    builder.adjust(2, 1)
    return builder.as_markup()

def get_admin_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="💰 Выдать баланс", callback_data="give_balance")
    builder.button(text="ℹ️ Инфо о пользователе", callback_data="get_user_info")
    builder.button(text="⚖️ Управление спорами", callback_data="manage_disputes")
    builder.button(text="🚨 Сбросить данные", callback_data="admin_reset_data_confirm") # Новая кнопка
    builder.adjust(1)
    return builder.as_markup()

def get_back_to_admin_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Назад в админ-меню", callback_data="admin_menu")
    return builder.as_markup()

def get_admin_reset_confirmation_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Да, сбросить", callback_data="admin_reset_data_execute")
    builder.button(text="❌ Нет, отмена", callback_data="admin_menu")
    builder.adjust(2)
    return builder.as_markup()

# --- СИСТЕМА ПОДДЕРЖКИ ---

def get_support_reply_keyboard(user_id):
    """Клавиатура для админа, чтобы ответить на тикет."""
    builder = InlineKeyboardBuilder()
    builder.button(text="Ответить пользователю", callback_data=f"answer_to_{user_id}")
    return builder.as_markup()

def get_cancel_support_keyboard():
    """Клавиатура для отмены создания тикета."""
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Отмена", callback_data="cancel_support")
    return builder.as_markup()


# --- ОСНОВНЫЕ МЕНЮ ---

def get_main_menu_inline():
    builder = InlineKeyboardBuilder()
    builder.button(text="🛒 Маркет", callback_data="market_menu")
    builder.button(text="👤 Профиль", callback_data="profile")
    builder.button(text="❓ Помощь", callback_data="help")
    builder.button(text="🤝 Поддержка", callback_data="support")
    builder.adjust(2)
    return builder.as_markup()

def get_market_menu_inline():
    builder = InlineKeyboardBuilder()
    builder.button(text="🟢 Купить", callback_data="buy_menu")
    builder.button(text="🔴 Продать", callback_data="sell_item")
    builder.button(text="⬅️ Назад в главное меню", callback_data="main_menu")
    builder.adjust(2, 1)
    return builder.as_markup()

def get_profile_keyboard(user_id):
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ Пополнить", callback_data="top_up_balance")
    builder.button(text="➖ Вывести", callback_data="withdraw_balance")
    builder.button(text="💼 Мои сделки", callback_data="my_deals")
    builder.button(text="⬅️ Назад в главное меню", callback_data="main_menu")
    builder.adjust(2, 1, 1)
    return builder.as_markup()

# --- ПРОЦЕСС ПОКУПКИ ---

def get_games_keyboard(games, callback_prefix="game_"):
    builder = InlineKeyboardBuilder()
    for game_id, game_name in games:
        builder.button(text=game_name, callback_data=f"{callback_prefix}{game_id}")
    
    if callback_prefix == "sell_game_":
        builder.button(text="⬅️ Назад в профиль", callback_data="profile")
    else:
        builder.button(text="⬅️ Назад в маркет", callback_data="market_menu")
    builder.adjust(1)
    return builder.as_markup()

def get_items_keyboard(items, game_id, page, total_items, per_page=5):
    builder = InlineKeyboardBuilder()
    for item in items:
        server_tag = f" ({item['server']})" if item.get('server') else ""
        builder.button(
            text=f"{item['name']}{server_tag} - {item['price']:.2f} RUB",
            callback_data=f"item_{item['id']}_{game_id}_{page}"
        )
    total_pages = (total_items + per_page - 1) // per_page
    pagination_buttons = []
    if page > 1:
        pagination_buttons.append(InlineKeyboardButton(text="⬅️", callback_data=f"items_page_{game_id}_{page-1}"))
    if total_pages > 1:
        pagination_buttons.append(InlineKeyboardButton(text=f"{page}/{total_pages}", callback_data="noop"))
    if page < total_pages:
        pagination_buttons.append(InlineKeyboardButton(text="➡️", callback_data=f"items_page_{game_id}_{page+1}"))

    if pagination_buttons:
        builder.row(*pagination_buttons)

    builder.button(text="⬅️ Назад к выбору игры", callback_data="buy_menu")
    builder.adjust(1)
    return builder.as_markup()

def get_open_sell_webapp_keyboard(game_id, game_name, server, web_app_url):
    """Создает клавиатуру с кнопкой для открытия Web App для продажи."""
    builder = InlineKeyboardBuilder()
    
    game_name_encoded = quote_plus(game_name)
    
    url = f"{web_app_url}/sell.html?gameId={game_id}&gameName={game_name_encoded}"
    
    if server:
        server_encoded = quote_plus(server)
        url += f"&server={server_encoded}"
        
    builder.button(
        text="📝 Заполнить детали товара",
        web_app=WebAppInfo(url=url)
    )
    builder.button(text="⬅️ Назад", callback_data="market_menu")
    builder.adjust(1)
    return builder.as_markup()

def get_item_details_keyboard(item_details, game_id, page, web_app_url):
    """Создает клавиатуру для страницы товара с кнопкой для Web App."""
    builder = InlineKeyboardBuilder()

    # Безопасно кодируем параметры для URL, чтобы избежать ошибок с символами
    item_name_encoded = quote_plus(item_details['name'])
    item_desc_encoded = quote_plus(item_details['description'])
    seller_username_encoded = quote_plus(item_details['seller_username'])

    # Формируем URL для Web App с правильными, camelCase параметрами, которые ожидает JS
    url = (
        f"{web_app_url}?itemId={item_details['id']}"
        f"&itemName={item_name_encoded}"
        f"&itemDescription={item_desc_encoded}"
        f"&itemPrice={item_details['price']}"
        f"&sellerUsername={seller_username_encoded}"
    )

    # Создаем кнопку, открывающую Web App
    web_app_button = InlineKeyboardButton(
        text="✅ Купить",
        web_app=WebAppInfo(url=url)
    )
    builder.row(web_app_button)

    # Кнопка "Назад" к списку товаров на той же странице
    builder.button(text="⬅️ Назад к товарам", callback_data=f"items_page_{game_id}_{page}")
    
    return builder.as_markup()

# --- ПРОЦЕСС ПРОДАЖИ ---

def get_sell_games_keyboard(games):
    """
    Создает клавиатуру для выбора игры в меню продажи.
    Использует общую функцию get_games_keyboard с префиксом для продажи.
    """
    return get_games_keyboard(games, callback_prefix="sell_game_")

def get_sell_servers_keyboard(game_id, servers, page=1, per_page=16):
    """Создает клавиатуру для выбора сервера с пагинацией."""
    builder = InlineKeyboardBuilder()
    
    start = (page - 1) * per_page
    end = start + per_page
    
    # Кнопки серверов
    for server in servers[start:end]:
        builder.button(text=server, callback_data=f"sell_server_{server}")
    
    builder.adjust(2) # По 2 сервера в ряд

    # Кнопки пагинации
    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"sell_server_page_{page - 1}"))
    if end < len(servers):
        nav_buttons.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=f"sell_server_page_{page + 1}"))
    
    if nav_buttons:
        builder.row(*nav_buttons)

    builder.button(text="⬅️ Назад к выбору игры", callback_data="sell_item")
    builder.adjust(1)
    return builder.as_markup()

def get_open_sell_form_keyboard(url):
    """Создает клавиатуру с кнопкой для открытия Web App (для игр без серверов)."""
    builder = InlineKeyboardBuilder()
    builder.button(
        text="📝 Заполнить информацию о товаре",
        web_app=WebAppInfo(url=url)
    )
    builder.button(text="⬅️ Назад к выбору игры", callback_data="sell_item")
    builder.adjust(1)
    return builder.as_markup()


# --- СДЕЛКИ ---

def get_deal_details_keyboard(deal_info, current_user_id):
    """Создает клавиатуру для страницы с деталями сделки."""
    builder = InlineKeyboardBuilder()
    status = deal_info['status']
    deal_id = deal_info['id']

    if status == 'in_progress':
        if current_user_id == deal_info['seller_id']:
            builder.button(text="✅ Я передал товар", callback_data=f"confirm_sent_{deal_id}")
        elif current_user_id == deal_info['buyer_id']:
            # Эта кнопка пока не нужна, покупатель ждет
            pass
    elif status == 'item_sent':
        if current_user_id == deal_info['buyer_id']:
            builder.button(text="✅ Я получил товар", callback_data=f"confirm_received_{deal_id}")
    
    # Кнопка спора доступна на определенных этапах
    if status in ['in_progress', 'item_sent']:
         builder.button(text="⚖️ Открыть спор", callback_data=f"open_dispute_{deal_id}")

    builder.button(text="⬅️ К моим сделкам", callback_data="my_deals")
    builder.adjust(1)
    return builder.as_markup()

    # Кнопка отмены
    builder.row(InlineKeyboardButton(text="❌ Отменить продажу", callback_data="cancel_sell_item"))

    return builder.as_markup()


def get_server_search_results_keyboard(found_servers):
    """Создает клавиатуру с результатами поиска серверов."""
    builder = InlineKeyboardBuilder()
    for server in found_servers[:24]: # Ограничиваем до 24 результатов, чтобы не было слишком много кнопок
        builder.button(text=server, callback_data=f"sell_server_{server}")
    builder.adjust(2)
    builder.row(InlineKeyboardButton(text="⬅️ К полному списку", callback_data="sell_server_show_full_list"))
    builder.row(InlineKeyboardButton(text="❌ Отменить продажу", callback_data="cancel_sell_item"))
    return builder.as_markup()


def get_server_search_failed_keyboard():
    """Создает клавиатуру для случая, когда поиск не дал результатов."""
    builder = InlineKeyboardBuilder()
    builder.button(text="🔄 Попробовать снова", callback_data="sell_server_search")
    builder.button(text="⬅️ К полному списку", callback_data="sell_server_show_full_list")

# --- УПРАВЛЕНИЕ СДЕЛКАМИ ---

def get_my_deals_keyboard(deals):
    builder = InlineKeyboardBuilder()
    if deals:
        for deal in deals:
            builder.button(
                text=f"Сделка #{deal['id']} - {deal['item_name']}", 
                callback_data=f"deal_details_{deal['id']}"
            )
        builder.adjust(1)
    builder.button(text="📜 История сделок", callback_data="deal_history")
    builder.button(text="⬅️ Назад в профиль", callback_data="profile")
    builder.adjust(1)
    return builder.as_markup()

def get_deal_history_keyboard(deals):
    builder = InlineKeyboardBuilder()
    for deal in deals:
        status_emoji = {'completed': '✅', 'cancelled': '❌'}.get(deal['status'], '❔')
        role_emoji = "🛒" if deal['role'] == 'purchase' else "💰"
        text = f"{status_emoji} {role_emoji} Сделка #{deal['id']} - {deal['item_name']} ({deal['status']})"
        builder.button(text=text, callback_data=f"deal_details_{deal['id']}")

    builder.button(text="⬅️ Назад к активным сделкам", callback_data="my_deals")
    builder.adjust(1)
    return builder.as_markup()

def get_deal_details_keyboard(deal_info, user_id):
    builder = InlineKeyboardBuilder()
    deal_id = deal_info['id']
    status = deal_info['status']
    is_buyer = user_id == deal_info['buyer_id']

    if status == 'in_progress':
        if not is_buyer:  # Продавец
            builder.button(text="✅ Я передал товар", callback_data=f"deal_action_sent_{deal_id}")
        builder.button(text="❌ Отменить сделку", callback_data=f"deal_action_cancel_{deal_id}")
        builder.button(text="❗️ Открыть спор", callback_data=f"deal_action_dispute_{deal_id}")

    elif status == 'item_sent':
        if is_buyer:  # Покупатель
            builder.button(text="✅ Я получил товар", callback_data=f"deal_action_confirm_{deal_id}")
        builder.button(text="❗️ Открыть спор", callback_data=f"deal_action_dispute_{deal_id}")

    # Кнопка "Назад" есть всегда
    builder.button(text="⬅️ Назад к сделкам", callback_data="my_deals")

    # Автоматически располагаем кнопки. Если есть кнопки действий, они будут сверху.
    # Если нет, то будет только кнопка "Назад".
    action_buttons_count = len(list(builder.buttons)) - 1  # Вычитаем кнопку "Назад"
    if action_buttons_count > 0:
        builder.adjust(*([1] * action_buttons_count), 1)  # Каждая кнопка действия в своей строке, кнопка Назад в своей
    else:
        builder.adjust(1)

    return builder.as_markup()

# --- FSM (ДЛЯ ОТМЕНЫ) ---

def get_cancel_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Отмена", callback_data="cancel_fsm")
    return builder.as_markup()


# --- ПРОЦЕСС ВЫВОДА СРЕДСТВ ---

def get_withdraw_country_keyboard(countries):
    builder = InlineKeyboardBuilder()
    for code, data in countries.items():
        builder.button(text=data['name'], callback_data=f"withdraw_country_{code}")
    builder.button(text="⬅️ Назад в профиль", callback_data="profile")
    builder.adjust(1)
    return builder.as_markup()

def get_withdraw_bank_keyboard(country_code, banks):
    builder = InlineKeyboardBuilder()
    for code, bank_data in banks.items():
        builder.button(text=bank_data['name'], callback_data=f"withdraw_bank_{country_code}_{code}")
    builder.button(text="⬅️ Назад к выбору страны", callback_data="withdraw_balance")
    builder.adjust(1)
    return builder.as_markup()

def get_withdraw_confirmation_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Подтвердить вывод", callback_data="confirm_withdrawal")
    builder.button(text="❌ Отменить", callback_data="profile")
    return builder.as_markup()


# --- ПРОЦЕСС ПОПОЛНЕНИЯ БАЛАНСА ---

def get_country_keyboard(countries):
    builder = InlineKeyboardBuilder()
    for code, data in countries.items():
        builder.button(text=data['name'], callback_data=f"deposit_country_{code}")
    builder.button(text="⬅️ Назад в профиль", callback_data="profile")
    builder.adjust(1)
    return builder.as_markup()

def get_bank_keyboard(country_code, banks):
    builder = InlineKeyboardBuilder()
    for code, bank_data in banks.items():
        builder.button(text=bank_data['name'], callback_data=f"deposit_bank_{country_code}_{code}")
    builder.button(text="⬅️ Назад к выбору страны", callback_data="top_up_balance")
    builder.adjust(1)
    return builder.as_markup()

def get_payment_confirmation_keyboard(country_code, bank_code):
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Я оплатил", callback_data="check_payment")
    builder.button(text="⬅️ Отменить и выбрать другой банк", callback_data=f"deposit_country_{country_code}")
    builder.adjust(1)
    return builder.as_markup()


# --- ОБЩИЕ КЛАВИАТУРЫ ---

def get_back_to_profile_keyboard():
    """Возвращает клавиатуру с кнопкой 'Назад в профиль'."""
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 Назад в профиль", callback_data="profile")
    return builder.as_markup()


def get_back_to_main_menu_keyboard():
    """Возвращает клавиатуру с кнопкой 'В главное меню'."""
    builder = InlineKeyboardBuilder()
    builder.button(text="🏠 В главное меню", callback_data="main_menu")
    return builder.as_markup()
