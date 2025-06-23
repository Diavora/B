# utils/db.py

import sqlite3

def init_db():
    conn = sqlite3.connect('swarovski_store.db')
    cur = conn.cursor()

    # Создаем таблицу пользователей
    cur.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        balance REAL DEFAULT 0,
        frozen_balance REAL DEFAULT 0,
        is_verified INTEGER DEFAULT 0,
        registration_date DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Создаем таблицу игр
    cur.execute('''
    CREATE TABLE IF NOT EXISTS games (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )
    ''')

    # Создаем таблицу товаров
    cur.execute('''
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL,
        server TEXT,
        game_id INTEGER NOT NULL,
        seller_id INTEGER,
        status TEXT DEFAULT 'on_sale', -- 'on_sale', 'in_deal', 'sold'
        listing_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (game_id) REFERENCES games (id),
        FOREIGN KEY (seller_id) REFERENCES users (user_id)
    )
    ''')

    # Создаем таблицу сделок
    cur.execute('''
    CREATE TABLE IF NOT EXISTS deals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER NOT NULL,
        buyer_id INTEGER NOT NULL,
        seller_id INTEGER, -- Может быть NULL для системных товаров
        price REAL NOT NULL,
        server TEXT,
        status TEXT DEFAULT 'in_progress', -- 'in_progress', 'completed', 'cancelled', 'dispute'
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (item_id) REFERENCES items (id),
        FOREIGN KEY (buyer_id) REFERENCES users (user_id),
        FOREIGN KEY (seller_id) REFERENCES users (user_id)
    )
    ''')

    # Миграция для таблицы deals
    cur.execute("PRAGMA table_info(deals)")
    columns = [column[1] for column in cur.fetchall()]
    if 'server' not in columns:
        print("Обновление базы данных: добавление столбца 'server' в таблицу 'deals'...")
        cur.execute("ALTER TABLE deals ADD COLUMN server TEXT")

    # Миграция для таблицы items
    cur.execute("PRAGMA table_info(items)")
    columns = [column[1] for column in cur.fetchall()]
    if 'server' not in columns:
        print("Обновление базы данных: добавление столбца 'server' в таблицу 'items'...")
        cur.execute("ALTER TABLE items ADD COLUMN server TEXT")

    # Миграция для таблицы users
    cur.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cur.fetchall()]
    if 'is_verified' not in columns:
        print("Обновление базы данных: добавление столбца 'is_verified' в таблицу 'users'...")
        cur.execute("ALTER TABLE users ADD COLUMN is_verified INTEGER DEFAULT 0")

    conn.commit()
    conn.close()


from .games_data import GAMES_DATA

def populate_initial_data():
    conn = sqlite3.connect('swarovski_store.db')
    cur = conn.cursor()

    for game_name, data in GAMES_DATA.items():
        # Проверяем, существует ли игра
        cur.execute("SELECT id FROM games WHERE name = ?", (game_name,))
        game_id_tuple = cur.fetchone()
        
        # Если игры нет, добавляем ее
        if not game_id_tuple:
            cur.execute("INSERT INTO games (name) VALUES (?)", (game_name,))
            game_id = cur.lastrowid
            print(f"Добавлена новая игра: {game_name}")
        else:
            game_id = game_id_tuple[0]

        # Определяем, где находится список товаров
        if isinstance(data, dict) and 'items' in data:
            items_list = data['items']
        else:
            items_list = data  # Старый формат

        # Добавляем товары для этой игры, если их еще нет
        for item in items_list:
            cur.execute("SELECT COUNT(*) FROM items WHERE name = ? AND game_id = ?", (item['name'], game_id))
            if cur.fetchone()[0] == 0:
                cur.execute(
                    "INSERT INTO items (name, description, price, game_id, seller_id, status, server) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (item['name'], item['description'], item['price'], game_id, None, 'on_sale', item.get('server'))
                )
                print(f"  - Добавлен товар: {item['name']}")

    conn.commit()
    conn.close()
    print("Проверка и заполнение начальными данными завершены.")


def add_user(user_id, username):
    conn = sqlite3.connect('swarovski_store.db')
    cur = conn.cursor()
    # При добавлении нового пользователя is_verified будет 0 (False)
    cur.execute("INSERT OR IGNORE INTO users (user_id, username, is_verified) VALUES (?, ?, 0)", (user_id, username))
    conn.commit()
    conn.close()

def is_user_verified(user_id):
    """Проверяет, прошел ли пользователь капчу."""
    conn = sqlite3.connect('swarovski_store.db')
    cur = conn.cursor()
    cur.execute("SELECT is_verified FROM users WHERE user_id = ?", (user_id,))
    result = cur.fetchone()
    conn.close()
    # Если пользователя нет или is_verified = 0, возвращаем False
    return result[0] == 1 if result else False

def verify_user(user_id):
    """Отмечает пользователя как прошедшего капчу."""
    conn = sqlite3.connect('swarovski_store.db')
    cur = conn.cursor()
    cur.execute("UPDATE users SET is_verified = 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def get_user_profile(user_id):
    conn = sqlite3.connect('swarovski_store.db')
    cur = conn.cursor()
    cur.execute("SELECT user_id, username, balance, frozen_balance, registration_date, is_verified FROM users WHERE user_id = ?", (user_id,))
    user_data = cur.fetchone()
    conn.close()
    if user_data:
        return {
            'user_id': user_data[0],
            'username': user_data[1],
            'balance': user_data[2],
            'frozen_balance': user_data[3],
            'registration_date': user_data[4],
            'is_verified': user_data[5]
        }
    return None

def get_user_deal_stats(user_id):
    """Получает статистику по сделкам пользователя."""
    conn = sqlite3.connect('swarovski_store.db')
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM deals WHERE (buyer_id = ? OR seller_id = ?) AND status = 'completed'", (user_id, user_id))
    completed_deals = cur.fetchone()[0]
    conn.close()
    return {'completed_deals': completed_deals}

def get_user_balance(user_id):
    """Получает текущий баланс пользователя."""
    conn = sqlite3.connect('swarovski_store.db')
    cur = conn.cursor()
    cur.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    result = cur.fetchone()
    conn.close()
    return result[0] if result else 0

def update_user_balance(user_id, amount_change):
    """Обновляет баланс пользователя на указанную величину (может быть отрицательной)."""
    conn = sqlite3.connect('swarovski_store.db')
    cur = conn.cursor()
    cur.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount_change, user_id))
    conn.commit()
    conn.close()

def get_item(item_id):
    """Получает данные о товаре по его ID."""
    conn = sqlite3.connect('swarovski_store.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM items WHERE id = ?", (item_id,))
    item = cur.fetchone()
    conn.close()
    return item

def create_deal(item_id, buyer_id, seller_id, price, server):
    """Создает новую запись о сделке."""
    conn = sqlite3.connect('swarovski_store.db')
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO deals (item_id, buyer_id, seller_id, price, server, status) VALUES (?, ?, ?, ?, ?, ?)",
        (item_id, buyer_id, seller_id, price, server, 'in_progress')
    )
    deal_id = cur.lastrowid
    conn.commit()
    conn.close()
    return deal_id

def update_item_status(item_id, new_status):
    """Обновляет статус товара."""
    conn = sqlite3.connect('swarovski_store.db')
    cur = conn.cursor()
    cur.execute("UPDATE items SET status = ? WHERE id = ?", (new_status, item_id))
    conn.commit()
    conn.close()

def get_games():
    conn = sqlite3.connect('swarovski_store.db')
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM games ORDER BY name")
    games = cur.fetchall()
    conn.close()
    return games

def get_items_by_game(game_id, page=1, per_page=5):
    offset = (page - 1) * per_page
    conn = sqlite3.connect('swarovski_store.db')
    conn.row_factory = sqlite3.Row  # Это позволит обращаться к колонкам по имени
    cur = conn.cursor()

    # Выбираем все товары, которые в продаже (и от системы, и от пользователей)
    cur.execute(
        "SELECT id, name, price, server FROM items WHERE game_id = ? AND status = 'on_sale' ORDER BY id DESC LIMIT ? OFFSET ?",
        (game_id, per_page, offset)
    )
    # Преобразуем результат в список словарей
    items = [dict(row) for row in cur.fetchall()]

    # Получаем общее количество всех товаров в этой категории для пагинации
    cur.execute("SELECT COUNT(*) FROM items WHERE game_id = ? AND status = 'on_sale'", (game_id,))
    total_items = cur.fetchone()[0]
    conn.close()
    return items, total_items

def update_item_status(item_id, new_status):
    """Обновляет статус товара (например, 'sold')."""
    conn = sqlite3.connect('swarovski_store.db')
    cur = conn.cursor()
    try:
        cur.execute("UPDATE items SET status = ? WHERE id = ?", (new_status, item_id))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()


def get_item_details(item_id):
    """Получает подробную информацию о товаре, включая имя продавца и название игры."""
    conn = sqlite3.connect('swarovski_store.db')
    cur = conn.cursor()
    cur.execute("""
        SELECT i.id, i.name, i.description, i.price, i.server, g.name as game_name, i.seller_id, u.username as seller_username, i.status
        FROM items i
        JOIN games g ON i.game_id = g.id
        LEFT JOIN users u ON i.seller_id = u.user_id
        WHERE i.id = ?
    """, (item_id,))
    item_data = cur.fetchone()
    conn.close()
    if not item_data:
        return None

    seller_username = item_data[7] if item_data[7] else "System"

    return {
        'id': item_data[0],
        'name': item_data[1],
        'description': item_data[2],
        'price': item_data[3],
        'server': item_data[4],
        'game_name': item_data[5],
        'seller_id': item_data[6],
        'seller_username': seller_username,
        'status': item_data[8]
    }


def add_item(game_id, seller_id, name, description, price, server=None):
    """
    Добавляет новый товар в базу данных, гарантируя сохранение транзакции.
    """
    conn = None
    try:
        conn = sqlite3.connect('swarovski_store.db')
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO items (game_id, seller_id, name, description, price, server, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (game_id, seller_id, name, description, price, server, 'on_sale')
        )
        item_id = cur.lastrowid
        conn.commit()
        print(f"DEBUG: Item committed to DB. ID: {item_id}")
        return item_id
    except sqlite3.Error as e:
        print(f"DATABASE ERROR in add_item: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            conn.close()


def create_deal(buyer_id, item_id):
    """Создает новую сделку, опционально с указанием сервера."""
    conn = sqlite3.connect('swarovski_store.db')
    cur = conn.cursor()
    try:
        conn.execute("BEGIN TRANSACTION")
        cur.execute("SELECT price, status, seller_id, server FROM items WHERE id = ?", (item_id,))
        item_info = cur.fetchone()
        if not item_info:
            return {'status': "item_not_found", 'data': None}
        
        item_price, item_status, seller_id, server = item_info
        
        if item_status != 'on_sale':
            return {'status': "item_not_available", 'data': None}

        cur.execute("SELECT balance FROM users WHERE user_id = ?", (buyer_id,))
        buyer_balance = cur.fetchone()
        if not buyer_balance or buyer_balance[0] < item_price:
            return {'status': "not_enough_funds", 'data': None}

        new_balance = buyer_balance[0] - item_price
        cur.execute("UPDATE users SET balance = ?, frozen_balance = frozen_balance + ? WHERE user_id = ?", 
                    (new_balance, item_price, buyer_id))

        cur.execute("UPDATE items SET status = 'in_deal' WHERE id = ?", (item_id,))

        cur.execute("INSERT INTO deals (item_id, buyer_id, seller_id, price, server, status) VALUES (?, ?, ?, ?, ?, ?)",
                    (item_id, buyer_id, seller_id, item_price, server, 'in_progress'))
        deal_id = cur.lastrowid

        conn.commit()
        deal_info = get_deal_info(deal_id)
        return {'status': "success", 'data': deal_info.get('data')}

    except sqlite3.Error as e:
        conn.rollback()
        print(f"Транзакция не удалась: {e}")
        return {'status': "db_error", 'data': None}
    finally:
        conn.close()

def get_deal_info(deal_id):
    """Получает подробную информацию о сделке."""
    conn = sqlite3.connect('swarovski_store.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT
                d.id, d.status, d.price, d.server, d.created_at, d.item_id,
                i.name as item_name,
                b.user_id as buyer_id, b.username as buyer_username,
                s.user_id as seller_id, s.username as seller_username
            FROM deals d
            JOIN items i ON d.item_id = i.id
            JOIN users b ON d.buyer_id = b.user_id
            LEFT JOIN users s ON d.seller_id = s.user_id
            WHERE d.id = ?
        """, (deal_id,))
        deal = cur.fetchone()
        if deal:
            return {'status': 'success', 'data': dict(deal)}
        else:
            return {'status': 'not_found', 'data': None}
    except sqlite3.Error as e:
        print(f"Database error in get_deal_info: {e}")
        return {'status': 'db_error', 'data': None}
    finally:
        conn.close()

def update_deal_status(deal_id, new_status, user_id):
    """Обновляет статус сделки, проверяя права пользователя."""
    conn = sqlite3.connect('swarovski_store.db')
    cur = conn.cursor()
    try:
        conn.execute("BEGIN TRANSACTION")
        
        deal_result = get_deal_info(deal_id)
        if deal_result['status'] != 'success':
            return deal_result
        
        deal = deal_result['data']

        if new_status == 'item_sent':
            if user_id != deal['seller_id']:
                return {'status': 'not_seller', 'data': deal}
            if deal['status'] != 'in_progress':
                return {'status': 'wrong_status', 'data': deal}

        cur.execute("UPDATE deals SET status = ? WHERE id = ?", (new_status, deal_id))
        conn.commit()
        
        return get_deal_info(deal_id)
        
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Database error in update_deal_status: {e}")
        return {'status': 'db_error', 'data': None}
    finally:
        conn.close()

def complete_deal(deal_id, user_id):
    """Завершает сделку."""
    conn = sqlite3.connect('swarovski_store.db')
    cur = conn.cursor()
    try:
        conn.execute("BEGIN TRANSACTION")
        
        deal_result = get_deal_info(deal_id)
        if deal_result['status'] != 'success':
            return deal_result
        
        deal = deal_result['data']

        if user_id != deal['buyer_id']:
            return {'status': 'not_buyer', 'data': deal}
        
        if deal['status'] != 'item_sent':
            return {'status': 'wrong_status', 'data': deal}

        # Перевод денег продавцу
        cur.execute("UPDATE users SET frozen_balance = frozen_balance - ? WHERE user_id = ?", (deal['price'], deal['buyer_id']))
        cur.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (deal['price'], deal['seller_id']))
        
        # Обновляем статус сделки и товара
        cur.execute("UPDATE deals SET status = 'completed' WHERE id = ?", (deal_id,))
        cur.execute("UPDATE items SET status = 'sold' WHERE id = ?", (deal['item_id'],))
        
        conn.commit()
        return get_deal_info(deal_id)
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Database error in complete_deal: {e}")
        return {'status': 'db_error', 'data': None}
    finally:
        conn.close()

def cancel_deal(deal_id, user_id):
    """Отменяет сделку."""
    conn = sqlite3.connect('swarovski_store.db')
    cur = conn.cursor()
    try:
        conn.execute("BEGIN TRANSACTION")

        deal_result = get_deal_info(deal_id)
        if deal_result['status'] != 'success':
            return deal_result

        deal = deal_result['data']

        if user_id not in [deal['buyer_id'], deal['seller_id']]:
            return {'status': "not_participant", 'data': deal}

        if deal['status'] not in ['in_progress', 'item_sent']:
            return {'status': "already_finalized", 'data': deal}

        cur.execute("UPDATE users SET balance = balance + ?, frozen_balance = frozen_balance - ? WHERE user_id = ?", (deal['price'], deal['price'], deal['buyer_id']))
        cur.execute("UPDATE deals SET status = 'cancelled' WHERE id = ?", (deal_id,))
        cur.execute("UPDATE items SET status = 'on_sale' WHERE id = ?", (deal['item_id'],))

        conn.commit()
        return get_deal_info(deal_id)
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Database error in cancel_deal: {e}")
        return {'status': "db_error", 'data': None}
    finally:
        conn.close()

def open_dispute(deal_id, user_id):
    conn = sqlite3.connect('swarovski_store.db')
    cur = conn.cursor()
    try:
        conn.execute("BEGIN TRANSACTION")
        
        deal_result = get_deal_info(deal_id)
        if deal_result['status'] != 'success':
            return deal_result

        deal = deal_result['data']

        if user_id not in [deal['buyer_id'], deal['seller_id']]:
            return {'status': "not_participant", 'data': deal}

        if deal['status'] not in ['in_progress', 'item_sent']:
            return {'status': "already_finalized", 'data': deal}

        cur.execute("UPDATE deals SET status = 'in_dispute' WHERE id = ?", (deal_id,))
        conn.commit()
        return get_deal_info(deal_id)
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Database error in open_dispute: {e}")
        return {'status': "db_error", 'data': None}
    finally:
        conn.close()

def get_admin_ids():
    from config import ADMIN_IDS
    return ADMIN_IDS

def get_user_deals(user_id, status=('in_progress', 'item_sent')):
    """
    Получает список сделок для пользователя с возможностью фильтрации по статусу.
    :param user_id: ID пользователя
    :param status: Кортеж статусов для фильтрации
    :return: Список словарей, представляющих сделки.
    """
    conn = sqlite3.connect('swarovski_store.db')
    conn.row_factory = sqlite3.Row  # Это позволит обращаться к колонкам по имени
    cur = conn.cursor()
    
    status_placeholders = ','.join('?' for _ in status)
    
    query = f"""
        SELECT
            d.id,
            i.name as item_name,
            d.price,
            d.status,
            d.server,
            CASE
                WHEN d.buyer_id = ? THEN 'purchase'
                WHEN d.seller_id = ? THEN 'sale'
            END as role
        FROM deals d
        JOIN items i ON d.item_id = i.id
        WHERE (d.buyer_id = ? OR d.seller_id = ?) AND d.status IN ({status_placeholders})
        ORDER BY d.created_at DESC
    """
    
    params = (user_id, user_id, user_id, user_id) + status
    
    cur.execute(query, params)
    # Преобразуем каждую строку в полноценный словарь для удобства
    deals = [dict(row) for row in cur.fetchall()]
    conn.close()
    return deals

def add_item(seller_id, game_id, name, description, price, server=None):
    conn = sqlite3.connect('swarovski_store.db')
    cur = conn.cursor()
    try:
        cur.execute(
        "INSERT INTO items (seller_id, game_id, name, description, price, server, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (seller_id, game_id, name, description, price, server, 'on_sale')
    )
        conn.commit()
        print(f"DEBUG: Committed item. Last row ID: {cur.lastrowid}")
        item_id = cur.lastrowid
        return item_id
    except sqlite3.Error as e:
        print(f"Ошибка при добавлении товара: {e}")
        return None
    finally:
        conn.close()

def get_disputed_deals():
    """Получает список всех сделок в статусе 'in_dispute'."""
    conn = sqlite3.connect('swarovski_store.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("""
        SELECT d.id, d.price, i.name as item_name, 
               b.user_id as buyer_id, b.username as buyer_username, 
               s.user_id as seller_id, s.username as seller_username
        FROM deals d
        JOIN items i ON d.item_id = i.id
        JOIN users b ON d.buyer_id = b.user_id
        LEFT JOIN users s ON d.seller_id = s.user_id
        WHERE d.status = 'in_dispute'
        ORDER BY d.created_at ASC
    """)
    disputes = [dict(row) for row in cur.fetchall()]
    conn.close()
    return disputes

def reset_all_user_data():
    """Обнуляет балансы и удаляет товары и сделки всех пользователей, не трогая системные товары."""
    conn = sqlite3.connect('swarovski_store.db')
    cur = conn.cursor()
    try:
        conn.execute("BEGIN TRANSACTION")
        # Обнуляем балансы всем пользователям
        cur.execute("UPDATE users SET balance = 0, frozen_balance = 0")
        # Удаляем только пользовательские товары (где есть seller_id)
        cur.execute("DELETE FROM items WHERE seller_id IS NOT NULL")
        # Удаляем только сделки между пользователями
        cur.execute("DELETE FROM deals WHERE seller_id IS NOT NULL")
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Ошибка при сбросе данных: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def resolve_dispute(deal_id, winner_id):
    """Решает спор в пользу указанного пользователя."""
    conn = sqlite3.connect('swarovski_store.db')
    cur = conn.cursor()
    try:
        conn.execute("BEGIN TRANSACTION")
        
        cur.execute("SELECT buyer_id, seller_id, item_id, price FROM deals WHERE id = ? AND status = 'in_dispute'", (deal_id,))
        deal = cur.fetchone()
        if not deal:
            return "deal_not_found"

        buyer_id, seller_id, item_id, price = deal

        if winner_id == buyer_id:
            # Покупатель прав - отменяем сделку, возвращаем деньги
            cur.execute("UPDATE users SET balance = balance + ?, frozen_balance = frozen_balance - ? WHERE user_id = ?", (price, price, buyer_id))
            cur.execute("UPDATE deals SET status = 'cancelled' WHERE id = ?", (deal_id,))
            cur.execute("UPDATE items SET status = 'on_sale' WHERE id = ?", (item_id,))
        elif winner_id == seller_id:
            # Продавец прав - завершаем сделку, переводим деньги
            cur.execute("UPDATE users SET frozen_balance = frozen_balance - ? WHERE user_id = ?", (price, buyer_id))
            if seller_id:
                cur.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (price, seller_id))
            cur.execute("UPDATE deals SET status = 'completed' WHERE id = ?", (deal_id,))
            cur.execute("UPDATE items SET status = 'sold' WHERE id = ?", (item_id,))
        else:
            # ID победителя не совпадает ни с покупателем, ни с продавцом
            conn.rollback()
            return "invalid_winner"

        conn.commit()
        return "success"
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Ошибка при разрешении спора по сделке {deal_id}: {e}")
        return "db_error"
    finally:
        conn.close()

def add_balance(user_id, amount):
    """
    Начисляет указанную сумму на баланс пользователя.
    :param user_id: ID пользователя
    :param amount: Сумма для начисления (может быть отрицательной для списания)
    :return: True, если операция успешна, False в противном случае.
    """
    conn = sqlite3.connect('swarovski_store.db')
    cur = conn.cursor()
    try:
        # Проверяем, существует ли пользователь
        cur.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
        if cur.fetchone() is None:
            return False # Пользователь не найден

        cur.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Ошибка при обновлении баланса для пользователя {user_id}: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()
