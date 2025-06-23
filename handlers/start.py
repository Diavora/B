# handlers/start.py
import random
import string

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, CallbackQuery, FSInputFile, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from keyboards.inline import get_main_menu_inline, get_market_menu_inline, get_back_to_main_menu_keyboard
from utils.db import add_user, is_user_verified, verify_user

router = Router()

class Captcha(StatesGroup):
    waiting_for_input = State()

CAPTCHA_EMOJIS = ["✅", "🤖", "✨", "💎", "🛒", "🎮", "👤", "🔴", "❓"]

def get_captcha_keyboard():
    """Генерирует клавиатуру для капчи с эмодзи."""
    emojis = random.sample(CAPTCHA_EMOJIS, 5)
    correct_emoji = random.choice(emojis)

    builder = InlineKeyboardBuilder()
    for emoji in emojis:
        builder.add(InlineKeyboardButton(text=emoji, callback_data=f"captcha:{emoji}"))
    
    builder.adjust(5) # 5 кнопок в ряд
    return builder.as_markup(), correct_emoji

WELCOME_TEXT = """
💎 <b>Добро пожаловать в Sacred Store!</b> 💎

Я ваш личный помощник в мире безопасной торговли игровыми ценностями.

<b>Что вы можете здесь делать?</b>
- <b>Покупать</b> редкие предметы с гарантией безопасности.
- <b>Продавать</b> свои игровые активы и зарабатывать.
- <b>Управлять</b> своим профилем и финансами.

Все сделки проходят через нашего гаранта, что обеспечивает максимальную защиту для обеих сторон.

👇 <b>Используйте меню ниже, чтобы начать.</b>
"""

HELP_TEXT = """
<b>❓ Помощь по боту</b>

Sacred Store — это безопасная площадка для покупки и продажи игровых ценностей.

<b>Основные разделы:</b>
🛒 <b>Маркет</b> — здесь вы можете просматривать товары, выбирать игры и совершать покупки.
👤 <b>Профиль</b> — ваш личный кабинет, где отображается баланс и история операций.
🔴 <b>Продать</b> — раздел для выставления ваших товаров на продажу.

<b>Как работает гарантия?</b>
1. Покупатель выбирает товар и нажимает "Купить".
2. Сумма сделки замораживается на балансе покупателя.
3. Продавец получает уведомление и передает товар покупателю.
4. Покупатель подтверждает получение товара, и деньги переводятся продавцу.
5. В случае проблем, вы можете открыть спор, и администрация поможет решить вопрос.

Если у вас остались вопросы, обратитесь в поддержку.
"""

async def show_welcome_message(message: Message):
    """Отправляет приветственное фото и меню, обрабатывая ошибку размера файла."""
    try:
        # Пытаемся отправить как фото (лимит 10МБ)
        await message.answer_photo(
            photo=FSInputFile("scar.png")
        )
    except TelegramBadRequest as e:
        # Если ошибка связана с размером файла, отправляем как документ (лимит 50МБ)
        if 'too big for a photo' in str(e):
            await message.answer_document(
                document=FSInputFile("scar.png")
            )
        else:
            # В случае других ошибок, можно их залогировать
            print(f"Произошла ошибка при отправке приветственного изображения: {e}")

    # Отправляем основной текст с меню
    await message.answer(
        text=WELCOME_TEXT,
        reply_markup=get_main_menu_inline(),
        parse_mode="HTML"
    )

@router.message(CommandStart())
async def start_command_handler(message: Message, state: FSMContext):
    """
    Обработчик команды /start.
    Проверяет, прошел ли пользователь капчу. Если нет - запускает ее.
    """
    user_id = message.from_user.id
    username = message.from_user.username
    add_user(user_id, username)

    if is_user_verified(user_id):
        await show_welcome_message(message)
    else:
        keyboard, correct_emoji = get_captcha_keyboard()
        await state.update_data(correct_emoji=correct_emoji)
        await state.set_state(Captcha.waiting_for_input)

        await message.answer(
            f"🤖 <b>Подтвердите, что вы не робот.</b>\n\n"
            f"Пожалуйста, нажмите на эмодзи: <b>{correct_emoji}</b>",
            reply_markup=keyboard,
            parse_mode="HTML"
        )

@router.callback_query(F.data.startswith("captcha:"), Captcha.waiting_for_input)
async def process_captcha_callback(callback: CallbackQuery, state: FSMContext):
    """
    Обрабатывает нажатие на кнопку капчи.
    """
    user_data = await state.get_data()
    correct_emoji = user_data.get('correct_emoji')
    chosen_emoji = callback.data.split(":")[1]

    if chosen_emoji == correct_emoji:
        verify_user(callback.from_user.id)
        await state.clear()
        await callback.message.edit_text("✅ <b>Спасибо! Верификация пройдена.</b>")
        await show_welcome_message(callback.message)
    else:
        # Неверный выбор, генерируем новую капчу
        keyboard, new_correct_emoji = get_captcha_keyboard()
        await state.update_data(correct_emoji=new_correct_emoji)
        await callback.message.edit_text(
            f"❌ <b>Неверно.</b> Попробуйте еще раз.\n\n"
            f"Пожалуйста, нажмите на эмодзи: <b>{new_correct_emoji}</b>",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    await callback.answer()

@router.callback_query(F.data == "main_menu")
async def main_menu_callback_handler(callback: CallbackQuery):
    await callback.message.edit_text(
        text=WELCOME_TEXT,
        reply_markup=get_main_menu_inline(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "market_menu")
async def market_menu_handler(callback: CallbackQuery):
    await callback.message.edit_text("Вы в разделе 'Маркет'.", reply_markup=get_market_menu_inline())
    await callback.answer()

@router.callback_query(F.data == "help")
async def help_handler(callback: CallbackQuery):
    await callback.message.edit_text(
        text=HELP_TEXT,
        reply_markup=get_back_to_main_menu_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()
