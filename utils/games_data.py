# utils/games_data.py

# Репрезентативный список игр и товаров с более реалистичными ценами и предметами.
# Цены указаны в рублях.
GAMES_DATA = {
    "Counter-Strike 2": [
        # Дешевые и распространенные скины
        {"name": "P250 | Sand Dune", "description": "Проверенный временем скин. Состояние: Field-Tested.", "price": 5},
        {"name": "SSG 08 | Abyss", "description": "Недорогой скин для снайперской винтовки. Состояние: Minimal Wear.", "price": 15},
        {"name": "UMP-45 | Carbon Fiber", "description": "Стильный и доступный скин. Состояние: Factory New.", "price": 25},
        {"name": "MAC-10 | Neon Rider", "description": "Яркий скин в стиле ретровейв. Состояние: Field-Tested.", "price": 600},

        # Средний ценовой сегмент
        {"name": "AK-47 | Slate", "description": "Полностью черный скин для AK-47. Состояние: Field-Tested.", "price": 250},
        {"name": "M4A4 | The Emperor", "description": "Скин, вдохновленный картами Таро. Состояние: Field-Tested.", "price": 1200},
        {"name": "AWP | Atheris", "description": "Изображение ядовитой змеи. Состояние: Minimal Wear.", "price": 350},

        # Более дорогие, но все еще доступные предметы
        {"name": "AK-47 | Redline", "description": "Классический и популярный скин. Состояние: Field-Tested.", "price": 1500},
        {"name": "M4A1-S | Cyrex", "description": "Футуристический дизайн в красно-черных тонах. Состояние: Minimal Wear.", "price": 1300},
        {"name": "AWP | Asiimov", "description": "Легендарный скин в стиле научной фантастики. Состояние: Battle-Scarred.", "price": 3000},

        # Ножи и перчатки (более дешевые варианты)
        {"name": "Navaja Knife | Forest DDPAT", "description": "Недорогой, но все же нож. Состояние: Battle-Scarred.", "price": 6000},
        {"name": "Hand Wraps | Duct Tape", "description": "Перчатки, которые выглядят... надежно. Состояние: Field-Tested.", "price": 5500}
    ],
    "Dota 2": [
        # Распространенные сеты и имморталки
        {"name": "Set: 'The Bone Scryer'", "description": "Набор предметов для Oracle.", "price": 50},
        {"name": "Immortal: 'Transversant Soul'", "description": "Immortal-предмет для Spectre.", "price": 30},
        {"name": "Taunt: 'Feeling Blue'", "description": "Насмешка для Storm Spirit.", "price": 15},

        # Более редкие и дорогие предметы
        {"name": "Set: 'The Magus Cypher'", "description": "Популярный набор для Rubick.", "price": 300},
        {"name": "Immortal: 'Mace of Aeons'", "description": "Immortal-предмет для Faceless Void.", "price": 1500},

        # Арканы и престижные предметы
        {"name": "Arcana: 'Manifold Paradox'", "description": "Arcana-предмет для Phantom Assassin.", "price": 2500},
        {"name": "Prestige Item: 'Axe Unleashed'", "description": "Престижный предмет для Axe (голый топор).", "price": 1800},

        # Курьеры
        {"name": "Courier: 'Amaterasu'", "description": "Курьер-волк из игры Okami.", "price": 700}
    ],
    "Escape from Tarkov": [
        # Расходники и бартер
        {"name": "Аптечка АИ-2", "description": "Базовая аптечка. Быстро лечит, но мало здоровья.", "price": 80},
        {"name": "Болты", "description": "Пачка болтов. Нужны для убежища и бартера.", "price": 150},
        {"name": "WD-40 100ml", "description": "Смазка, необходимая для некоторых квестов и крафтов.", "price": 200},
        
        # Ключи и экипировка среднего уровня
        {"name": "Бронежилет 6Б13 'Кираса'", "description": "Надежный бронежилет 4 класса.", "price": 900},
        {"name": "Ключ от выхода на электростанцию", "description": "Позволяет выйти с карты 'Берег' через ГЭС.", "price": 1500},
        {"name": "Светодиодная линза (LedX)", "description": "Критически важный предмет для квестов и убежища.", "price": 9500},

        # Топовые и редкие предметы
        {"name": "Тепловизионный прицел T-7", "description": "Позволяет видеть врагов по их тепловой сигнатуре.", "price": 20000},
        {"name": "Кейс для вещей THICC", "description": "Огромный кейс для хранения предметов в схроне.", "price": 150000},
        {"name": "Лабораторная ключ-карта (Красная)", "description": "Одна из самых редких и дорогих ключ-карт.", "price": 600000}
    ],
    "World of Warcraft": [
        # Расходники и материалы
        {"name": "Жетон WoW", "description": "Позволяет оплатить 30 дней игрового времени или пополнить кошелек Battle.net.", "price": 1500},
        {"name": "Настой вечной силы (20 шт.)", "description": "Увеличивает основную характеристику на час. Для рейдов и подземелий.", "price": 1200},
        {"name": "Теневая ткань (100 шт.)", "description": "Ценный материал для портняжного дела.", "price": 800},

        # Экипировка (BoE)
        {"name": "Кольцо затухающей магии", "description": "Эпическое кольцо с хорошими характеристиками (BoE).", "price": 5000},
        {"name": "Боевые рукавицы вечного гладиатора", "description": "Эпические латные перчатки (BoE).", "price": 2500},

        # Питомцы и транспорт
        {"name": "Боевой питомец: Спектральный тигренок", "description": "Редкий и милый спутник.", "price": 3000},
        {"name": "Поводья Вульпина-сердцееда", "description": "Популярное и красивое верховое животное.", "price": 4000},
        {"name": "Поводья стремительного призрачного тигра", "description": "Чрезвычайно редкое верховое животное из TCG.", "price": 15000}
    ],
    "Rust": [
        # Дешевые скины
        {"name": "Tempered Revolver", "description": "Простой скин на револьвер.", "price": 80},
        {"name": "Forest Camo Hoodie", "description": "Камуфляжный худи для маскировки.", "price": 150},

        # Средний ценовой сегмент
        {"name": "Glory AK47", "description": "Популярный и красивый скин на AK-47.", "price": 500},
        {"name": "Blackout Facemask", "description": "Полностью черная маска.", "price": 1200},

        # Дорогие скины
        {"name": "Punishment Mask", "description": "Очень редкая и дорогая маска.", "price": 5000},
        {"name": "Big Grin", "description": "Легендарная маска на металлическую лицевую пластину.", "price": 8000}
    ],
    "VALORANT": [
        # Популярные скины
        {"name": "Vandal 'Reaver'", "description": "Один из самых любимых скинов сообщества.", "price": 1775},
        {"name": "Phantom 'Oni'", "description": "Скин в японском стиле с маской демона.", "price": 1775},
        {"name": "Operator 'Ion'", "description": "Футуристический и минималистичный дизайн.", "price": 1775},

        # Ножи
        {"name": "Нож 'Коготь Они'", "description": "Коготь в стиле демона Они.", "price": 3550},
        {"name": "Карамбит 'Жнец'", "description": "Изогнутый нож из набора 'Reaver'.", "price": 4350}
    ],
    "Apex Legends": [
        # Валюта и реликвии
        {"name": "1000 монет Apex", "description": "Внутриигровая валюта для покупки скинов и пропусков.", "price": 750},
        {"name": "Реликвия: Кунай Рэйф", "description": "Легендарный нож для персонажа Wraith.", "price": 10000},
        
        # Скины на оружие
        {"name": "R-301 'Ледяной дракон'", "description": "Легендарный скин на карабин R-301.", "price": 1800},
        {"name": "Wingman 'Беспощадное крыло'", "description": "Реактивный скин на Wingman.", "price": 1800},

        # Скины персонажей
        {"name": "Октейн 'Эль-диабло'", "description": "Дьявольский скин для Октейна.", "price": 1200}
    ],
    "Team Fortress 2": [
        # Ключи и валюта
        {"name": "Ключ от ящика Манн Ко", "description": "Открывает любой ящик Манн Ко.", "price": 150},
        {"name": "Очищенный металл (10 шт.)", "description": "Основная валюта для обмена между игроками.", "price": 20},

        # Оружие
        {"name": "Сковорода", "description": "Просто сковорода. Но какая!", "price": 50},
        {"name": "Австралийский ракетомет", "description": "Блестящий и смертоносный. Покрыт австралием.", "price": 4000},

        # Косметика
        {"name": "Нимб праведника", "description": "Классическая шапка, которая подойдет всем.", "price": 300},
        {"name": "Необычная шляпа: Горящие огни", "description": "Шапка с редким эффектом 'Burning Flames'.", "price": 25000}
    ],
    "Genshin Impact": [
        # Валюта
        {"name": "Благословение полой луны", "description": "Дает 90 Камней Истока ежедневно в течение 30 дней.", "price": 450},
        {"name": "6480 Кристаллов сотворения", "description": "Большой пакет внутриигровой валюты.", "price": 9000},

        # Прочее
        {"name": "Боевой пропуск 'Жемчужный гимн'", "description": "Открывает премиальные награды боевого пропуска.", "price": 900},
        {"name": "Скин: 'Пурпурный гром' (Кэ Цин)", "description": "Эксклюзивный наряд для персонажа Кэ Цин.", "price": 1500}
    ],
    "PUBG: BATTLEGROUNDS": [
        # Скины на оружие
        {"name": "AKM 'Золотая ярость'", "description": "Позолоченный скин на AKM.", "price": 800},
        {"name": "M416 'Шут'", "description": "Яркий и популярный скин на M416.", "price": 1200},

        # Одежда
        {"name": "Костюм 'Диноленд'", "description": "Забавный костюм динозавра.", "price": 1000},
        {"name": "Маска 'Кролик-убийца'", "description": "Устрашающая маска кролика.", "price": 500}
    ],
    "Fortnite": [
        # Валюта
        {"name": "1000 В-баксов", "description": "Внутриигровая валюта Fortnite.", "price": 600},
        {"name": "5000 В-баксов", "description": "Большой пакет внутриигровой валюты.", "price": 2400},

        # Скины и наборы
        {"name": "Скин 'Человек-паук'", "description": "Экипировка Человека-паука.", "price": 1500},
        {"name": "Набор 'Темный огонь'", "description": "Набор из нескольких легендарных предметов.", "price": 2000},
        {"name": "Боевой пропуск", "description": "Доступ к наградам текущего сезона.", "price": 950}
    ],
    "Overwatch 2": [
        # Валюта и прочее
        {"name": "1000 монет Overwatch", "description": "Внутриигровая валюта Overwatch 2.", "price": 750},
        {"name": "Премиальный боевой пропуск", "description": "Доступ к премиальным наградам сезона.", "price": 1000},

        # Скины
        {"name": "Скин 'Розовая лента' (Ангел)", "description": "Легендарный благотворительный скин для Ангела.", "price": 1500},
        {"name": "Скин 'Кибердемон' (Гэндзи)", "description": "Мифический скин для Гэндзи.", "price": 2500},
        {"name": "Скин 'Атлантика' (Трейсер)", "description": "Эксклюзивный скин лиги Overwatch.", "price": 1800}
    ],
    "Sea of Thieves": [
        # Валюта и прочее
        {"name": "1000 Древних монет", "description": "Премиальная валюта для покупки предметов в пиратской лавке.", "price": 800},
        {"name": "Пропуск грабителей", "description": "Доступ к премиальным наградам сезона.", "price": 1000},

        # Косметика
        {"name": "Паруса 'Темные войны'", "description": "Эксклюзивные паруса для корабля.", "price": 600},
        {"name": "Корпус 'Пепельный дракон'", "description": "Устрашающий корпус для корабля.", "price": 600},
        {"name": "Питомец: Обезьянка-капуцин", "description": "Верный спутник в ваших приключениях.", "price": 500}
    ],
    "Call of Duty: Warzone": [
        # Валюта и прочее
        {"name": "2400 очков Call of Duty", "description": "Внутриигровая валюта (CP).", "price": 1500},
        {"name": "Боевой пропуск 'BlackCell'", "description": "Премиальный боевой пропуск с эксклюзивными наградами.", "price": 2500},

        # Наборы
        {"name": "Набор оперативника 'Гоуст'", "description": "Классический скин для оперативника Гоуст.", "price": 2000},
        {"name": "Чертеж оружия 'M4 - Ожог'", "description": "Легендарный чертеж для M4 с трассерами.", "price": 1800}
    ],
    "Black Russia": {
        "requires_server": True,
        "servers": [
            "RED", "GREEN", "BLUE", "YELLOW", "ORANGE", "PURPLE", "LIME", "PINK", "CHERRY", "BLACK", "INDIGO", "WHITE", "MAGENTA", "CRIMSON", "GOLD", "AZURE", "PLATINUM", "AQUA", "GRAY", "ICE", "CHILLI", "CHOCO", "MOSCOW", "SPB", "UFA", "SOCHI", "KAZAN", "SAMARA", "ROSTOV", "ANAPA", "EKB", "KRASNODAR", "ARZAMAS", "NOVOSIB", "GROZNY", "SARATOV", "OMSK", "IRKUTSK", "VOLGOGRAD", "VORONEZH", "BELGOROD", "KALININGRAD", "VLADIVOSTOK", "VLADIKAVKAZ", "MAKHCHKALA", "KHABAROVSK", "CHEBOKSARY", "KRASNOYARSK", "CHELYABINSK",
            "MURMANSK", "RYAZAN", "TULA", "PERM", "ORENBURG", "ARKHANGELSK", "KURSK", "PENZA", "TOLYATTI", "TYUMEN", "KEMEROVO", "KIROV", "PSKOV", "SMOLENSK", "STAVROPOL", "IVANOVO", "BARNAUL", "YAROSLAVL", "OREL", "BRYANSK", "TAMBOV", "YAKUTSK", "ULYANOVSK", "LIPETSK", "KOSTROMA", "CHITA", "ASTRAKHAN", "BRATSK", "TAGANROG", "NOVGOROD", "KALUGA", "VLADIMIR", "IZHEVSK", "TOMSK", "TVER", "VOLOGDA", "CHEREPOVETS", "MAGADAN", "PODOLSK", "SURGUT"
        ],
        "items": [
            {"name": "Игровая валюта (1 млн)", "description": "1,000,000 игровой валюты.", "price": 100},
            {"name": "Игровая валюта (5 млн)", "description": "5,000,000 игровой валюты.", "price": 450},
            {"name": "Игровая валюта (10 млн)", "description": "10,000,000 игровой валюты.", "price": 850},
            {"name": "Эксклюзивный автомобиль 'Lotus'", "description": "Редкий автомобиль Lotus.", "price": 1500},
            {"name": "Скин 'Бандит'", "description": "Скин.", "price": 1150},
            {"name": "Акк с 18 лвлом", "description": "18 лвл без привязок", "price": 1000},
            {"name": "БП и 8 ЛВЛ", "description": "Привязка тг ккуплен бп", "price": 600},
            {"name": "Акк с 18 лвлом", "description": "18 лвл без привязок", "price": 800},
            {"name": "Ламба URUS", "description": "Выдам быстро на авторынке", "price": 1900},
            {"name": "Личный акк своя семья", "description": "владелец т4 семьи автопарк на 20кк", "price": 3000}
        ]
    }
}
