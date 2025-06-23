# utils/payment_data.py

PAYMENT_SYSTEMS = {
    'ru': {
        'name': '🇷🇺 Россия',
        'currency': 'RUB',
        'banks': {
            'sber': 'Сбербанк',
            'tinkoff': 'Тинькофф',
            'alfabank': 'Альфа-Банк'
        },
        'requisites': {
            'sber': 'Номер карты Сбербанк: `2202 2000 1234 5678`',
            'tinkoff': 'Номер карты Тинькофф: `2200 7000 9876 5432`',
            'alfabank': 'Номер счета Альфа-Банк: `40817810504000012345`'
        }
    },
    'ua': {
        'name': '🇺🇦 Украина',
        'currency': 'UAH',
        'banks': {
            'privat': 'ПриватБанк',
            'mono': 'monobank'
        },
        'requisites': {
            'privat': 'Номер карты ПриватБанк: `4149 4990 1111 2222`',
            'mono': 'Номер карты monobank: `5375 4100 3333 4444`'
        }
    },
    'kz': {
        'name': '🇰🇿 Казахстан',
        'currency': 'KZT',
        'banks': {
            'kaspi': 'Kaspi Bank',
            'halyk': 'Halyk Bank'
        },
        'requisites': {
            'kaspi': 'Номер телефона Kaspi: `+7 (707) 123-45-67`',
            'halyk': 'Номер счета Halyk Bank: `KZ123456789012345678`'
        }
    }
}
