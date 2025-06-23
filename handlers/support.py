# handlers/support.py

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.filters import BaseFilter

from config import ADMIN_IDS
from keyboards.inline import get_support_reply_keyboard, get_cancel_support_keyboard, get_main_menu_inline
from handlers.start import WELCOME_TEXT

router = Router()

# --- FSM для системы поддержки ---
class SupportStates(StatesGroup):
    writing_question = State() # Состояние, когда пользователь пишет вопрос
    writing_answer = State()   # Состояние, когда админ пишет ответ

# --- Фильтр для проверки на админа ---
class IsAdmin(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in ADMIN_IDS

# 1. Пользователь нажимает кнопку "Поддержка"
@router.callback_query(F.data == "support")
async def start_support(callback: CallbackQuery, state: FSMContext):
    await state.set_state(SupportStates.writing_question)
    await callback.message.edit_text(
        "Напишите ваш вопрос, и он будет отправлен администратору. Мы постараемся ответить как можно скорее.",
        reply_markup=get_cancel_support_keyboard()
    )
    await callback.answer()

# 2. Пользователь отправляет свой вопрос
@router.message(SupportStates.writing_question)
async def question_sent(message: Message, state: FSMContext, bot: Bot):
    # Выходим из состояния, чтобы пользователь мог дальше пользоваться ботом
    await state.clear()

    user_info = f"Пользователь: @{message.from_user.username} (ID: {message.from_user.id})"

    # Отправляем всем админам
    for admin_id in ADMIN_IDS:
        try:
            # Пересылаем сообщение, чтобы сохранить форматирование и медиа
            await bot.forward_message(chat_id=admin_id, from_chat_id=message.chat.id, message_id=message.message_id)
            # Отправляем сообщение с информацией и кнопкой ответа
            await bot.send_message(
                admin_id,
                f"Новый вопрос в поддержку от {user_info}",
                reply_markup=get_support_reply_keyboard(message.from_user.id)
            )
        except Exception as e:
            print(f"Не удалось отправить сообщение админу {admin_id}: {e}")

    await message.answer("✅ Ваш вопрос отправлен администратору. Ожидайте ответа.", reply_markup=get_main_menu_inline())

# 3. Админ нажимает "Ответить пользователю"
@router.callback_query(F.data.startswith("answer_to_"), IsAdmin())
async def prompt_admin_answer(callback: CallbackQuery, state: FSMContext):
    user_id = int(callback.data.split("_")[2])
    await state.set_state(SupportStates.writing_answer)
    # Сохраняем ID пользователя, которому нужно ответить
    await state.update_data(user_to_answer=user_id)
    await callback.message.answer(f"Введите ваш ответ для пользователя с ID {user_id}:")
    # Убираем кнопку "Ответить" после нажатия
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer()

# 4. Админ отправляет ответ
@router.message(SupportStates.writing_answer, IsAdmin())
async def send_answer_to_user(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    user_id = data.get("user_to_answer")

    if not user_id:
        await message.answer("Произошла ошибка, не найден ID пользователя для ответа.")
        await state.clear()
        return

    try:
        # Пересылаем ответ админа пользователю
        await bot.send_message(user_id, "Ответ от поддержки:")
        await bot.forward_message(chat_id=user_id, from_chat_id=message.chat.id, message_id=message.message_id)
        await message.answer(f"✅ Ваш ответ успешно отправлен пользователю {user_id}.")
    except Exception as e:
        await message.answer(f"❌ Не удалось отправить ответ пользователю {user_id}. Ошибка: {e}")

    # Очищаем состояние после ответа
    await state.clear()

# 5. Отмена создания тикета
@router.callback_query(F.data == "cancel_support")
async def cancel_support_creation(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    # Возвращаем в главное меню
    await callback.message.edit_text(
        text=WELCOME_TEXT,
        reply_markup=get_main_menu_inline()
    )
    await callback.answer()
