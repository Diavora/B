# config.py

BOT_TOKEN = "7839428354:AAFVfPYMjh2G92IJN2OUVcz9ozcQsMHCzvk"  # Вставьте сюда токен вашего бота

# Впишите сюда через запятую числовые ID администраторов бота
# Пример: ADMIN_IDS = [123456789, 987654321]
ADMIN_IDS = [8043784997]

# URL веб-приложения (сюда нужно вставить URL от ngrok)
WEB_APP_URL = "https://diavora.github.io/B/"
SELLING_PRICE_COMMISSION = 5 # Комиссия в процентах (например, 5%)

# Словать с платежными системами для вывода
PAYMENT_SYSTEMS = {
    'RU': {
        'name': '🇷🇺 Россия',
        'currency': 'RUB',
        'banks': {
            'sber': {'name': 'Сбербанк', 'requisites': '2202 2008 1234 5678'},
            'tinkoff': {'name': 'Тинькофф', 'requisites': '5536 9100 1234 5678'},
            'alpha': {'name': 'Альфа-Банк', 'requisites': '5559 4900 1234 5678'}
        }
    },
    'KZ': {
        'name': '🇰🇿 Казахстан',
        'currency': 'KZT',
        'banks': {
            'kaspi': {'name': 'Kaspi Bank', 'requisites': '4400 4300 1234 5678'},
            'halyk': {'name': 'Halyk Bank', 'requisites': '4652 4200 1234 5678'}
        }
    },
    'UA': {
        'name': '🇺🇦 Украина',
        'currency': 'UAH',
        'banks': {
            'privat': {'name': 'ПриватБанк', 'requisites': '4149 4300 1234 5678'},
            'mono': {'name': 'monobank', 'requisites': '5375 4100 1234 5678'}
        }
    }
}
