# restore_items.py

import sqlite3
import sys
import os

# Добавляем корневую директорию проекта в sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.games_data import GAMES_DATA

def restore_bot_items():
    db_path = 'swarovski_store.db'
    print(f"Подключение к базе данных: {db_path}")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    try:
        print("Начинаем восстановление системных товаров...")
        # Сначала безопасно удаляем существующие системные товары, чтобы избежать дубликатов
        cur.execute("DELETE FROM items WHERE seller_id IS NULL")
        print(f"{cur.rowcount} старых системных товаров удалено.")

        # Заново добавляем товары из games_data
        items_added_count = 0
        for game_name, items_list in GAMES_DATA.items():
            cur.execute("SELECT id FROM games WHERE name = ?", (game_name,))
            game_id_tuple = cur.fetchone()
            
            if not game_id_tuple:
                print(f"Игра '{game_name}' не найдена. Пропускаем товары для нее.")
                continue
            game_id = game_id_tuple[0]

            for item in items_list:
                cur.execute(
                    "INSERT INTO items (name, description, price, game_id, seller_id, status) VALUES (?, ?, ?, ?, ?, ?)",
                    (item['name'], item['description'], item['price'], game_id, None, 'on_sale')
                )
                items_added_count += 1
        
        conn.commit()
        print(f"Успешно добавлено {items_added_count} новых системных товаров.")
        print("Системные товары были успешно восстановлены.")

    except sqlite3.Error as e:
        print(f"Произошла ошибка SQLite при восстановлении товаров: {e}")
        conn.rollback()
    except Exception as e:
        print(f"Произошла непредвиденная ошибка: {e}")
        conn.rollback()
    finally:
        conn.close()
        print("Соединение с базой данных закрыто.")

if __name__ == "__main__":
    restore_bot_items()
