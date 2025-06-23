# handlers/admin.py

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, BaseFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import ADMIN_IDS
from keyboards.inline import get_admin_keyboard, get_back_to_admin_menu_keyboard, get_disputes_list_keyboard, get_dispute_resolution_keyboard, get_admin_reset_confirmation_keyboard
from utils.db import get_user_profile, add_balance, get_disputed_deals, resolve_dispute, get_deal_info, reset_all_user_data

# --- Фильтр для проверки на админа ---
class IsAdmin(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in ADMIN_IDS

router = Router()

# --- Состояния для FSM ---
class AdminStates(StatesGroup):
    give_balance_user_id = State()
    give_balance_amount = State()
    get_user_info = State()

# --- Главное меню админки ---
@router.message(Command("admin"), IsAdmin())
async def admin_panel_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Добро пожаловать в админ-панель!", reply_markup=get_admin_keyboard())

@router.callback_query(F.data == "admin_menu", IsAdmin())
async def admin_panel_callback_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Добро пожаловать в админ-панель!", reply_markup=get_admin_keyboard())

# --- Раздел "Информация о пользователе" ---
@router.callback_query(F.data == "get_user_info", IsAdmin())
async def get_user_info_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.get_user_info)
    await callback.message.edit_text("Введите User ID пользователя, чтобы получить информацию о нем:", reply_markup=get_back_to_admin_menu_keyboard())

@router.message(AdminStates.get_user_info, IsAdmin())
async def process_user_info_id(message: Message, state: FSMContext):
    try:
        user_id = int(message.text)
    except ValueError:
        await message.answer("Неверный формат ID. Пожалуйста, введите число.", reply_markup=get_back_to_admin_menu_keyboard())
        return

    user_profile = get_user_profile(user_id)

    if user_profile:
        text = (
            f"<b>Профиль пользователя:</b> <code>{user_id}</code>\n"
            f"<b>Username:</b> @{user_profile['username']}\n"
            f"<b>Баланс:</b> {user_profile['balance']:.2f} RUB\n"
            f"<b>Заморожено:</b> {user_profile['frozen_balance']:.2f} RUB\n"
            f"<b>Дата регистрации:</b> {user_profile['registration_date']}"
        )
        await message.answer(text, parse_mode="HTML", reply_markup=get_back_to_admin_menu_keyboard())
    else:
        await message.answer("Пользователь с таким ID не найден.", reply_markup=get_back_to_admin_menu_keyboard())
    
    await state.clear()

# --- Раздел "Выдать баланс" ---
@router.callback_query(F.data == "give_balance", IsAdmin())
async def give_balance_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.give_balance_user_id)
    await callback.message.edit_text("Введите User ID пользователя, которому хотите начислить баланс:", reply_markup=get_back_to_admin_menu_keyboard())

@router.message(AdminStates.give_balance_user_id, IsAdmin())
async def process_give_balance_user_id(message: Message, state: FSMContext):
    try:
        user_id = int(message.text)
        if not get_user_profile(user_id):
            await message.answer("Пользователь с таким ID не найден. Попробуйте еще раз:", reply_markup=get_back_to_admin_menu_keyboard())
            return
    except ValueError:
        await message.answer("Неверный формат ID. Пожалуйста, введите число.", reply_markup=get_back_to_admin_menu_keyboard())
        return

    await state.update_data(user_id_to_add=user_id)
    await state.set_state(AdminStates.give_balance_amount)
    await message.answer(f"Отлично. Теперь введите сумму для начисления пользователю <code>{user_id}</code>.", parse_mode="HTML", reply_markup=get_back_to_admin_menu_keyboard())

@router.message(AdminStates.give_balance_amount, IsAdmin())
async def process_give_balance_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text.replace(',', '.'))
    except ValueError:
        await message.answer("Неверный формат суммы. Пожалуйста, введите число.", reply_markup=get_back_to_admin_menu_keyboard())
        return

    data = await state.get_data()
    user_id = data.get('user_id_to_add')

    if add_balance(user_id, amount):
        await message.answer(f"Баланс в размере <b>{amount:.2f} RUB</b> успешно начислен пользователю <code>{user_id}</code>.", parse_mode="HTML", reply_markup=get_back_to_admin_menu_keyboard())
        try:
            await message.bot.send_message(user_id, f"Вам было начислено <b>{amount:.2f} RUB</b> администратором.", parse_mode="HTML")
        except Exception as e:
            await message.answer("(Не удалось уведомить пользователя)", reply_markup=get_back_to_admin_menu_keyboard())
    else:
        await message.answer("Произошла ошибка при начислении баланса. Проверьте логи.", reply_markup=get_back_to_admin_menu_keyboard())

    await state.clear()


# --- Раздел "Управление спорами" ---

@router.callback_query(F.data == "manage_disputes", IsAdmin())
async def manage_disputes_handler(callback: CallbackQuery):
    disputes = get_disputed_deals()
    if not disputes:
        await callback.message.edit_text(
            "Активных споров нет.",
            reply_markup=get_back_to_admin_menu_keyboard()
        )
        return
    
    await callback.message.edit_text(
        "<b>Активные споры:</b>",
        reply_markup=get_disputes_list_keyboard(disputes),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("admin_dispute_"), IsAdmin())
async def show_dispute_details_handler(callback: CallbackQuery):
    deal_id = int(callback.data.split("_")[2])
    result = get_deal_info(deal_id)

    if result['status'] != 'success':
        await callback.answer("Сделка не найдена.", show_alert=True)
        return

    deal_info = result['data']

    if deal_info['status'] != 'in_dispute':
        await callback.answer("Спор по этой сделке не открыт или уже разрешен.", show_alert=True)
        return

    text = (
        f"<b>Разбор спора по сделке #{deal_id}</b>\n\n"
        f"<b>Покупатель:</b> @{deal_info['buyer_username']} (<code>{deal_info['buyer_id']}</code>)\n"
        f"<b>Продавец:</b> @{deal_info['seller_username']} (<code>{deal_info['seller_id']}</code>)\n"
        f"<b>Товар:</b> {deal_info['item_name']}\n"
        f"<b>Цена:</b> {deal_info['price']:.2f} RUB\n\n"
        f"Выберите, в чью пользу разрешить спор:"
    )

    await callback.message.edit_text(
        text,
        reply_markup=get_dispute_resolution_keyboard(deal_id, deal_info['buyer_id'], deal_info['seller_id']),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("resolve_"), IsAdmin())
async def resolve_dispute_handler(callback: CallbackQuery, bot: Bot):
    try:
        _, deal_id_str, _, winner_id_str = callback.data.split("_")
        deal_id = int(deal_id_str)
        winner_id = int(winner_id_str)
    except (ValueError, IndexError):
        await callback.answer("Ошибка в данных для разрешения спора.", show_alert=True)
        return

    result = get_deal_info(deal_id)
    if result['status'] != 'success':
        await callback.answer("Сделка не найдена.", show_alert=True)
        return
    
    deal_info = result['data']

    loser_id = deal_info['seller_id'] if winner_id == deal_info['buyer_id'] else deal_info['buyer_id']
    
    resolve_result = resolve_dispute(deal_id, winner_id)

    if resolve_result == "success":
        winner_username = deal_info['buyer_username'] if winner_id == deal_info['buyer_id'] else deal_info['seller_username']
        await callback.message.edit_text(f"✅ Спор по сделке #{deal_id} успешно разрешен в пользу @{winner_username}.", reply_markup=get_back_to_admin_menu_keyboard())

        # Уведомляем победителя и проигравшего
        try:
            await bot.send_message(winner_id, f"<b>Поздравляем!</b>\nСпор по сделке #{deal_id} разрешен в вашу пользу.", parse_mode="HTML")
            await bot.send_message(loser_id, f"<b>К сожалению.</b>\nСпор по сделке #{deal_id} разрешен не в вашу пользу.", parse_mode="HTML")
        except Exception as e:
            print(f"Ошибка при отправке уведомлений о решении спора: {e}")

    else:
        await callback.answer(f"Не удалось разрешить спор. Ошибка: {resolve_result}", show_alert=True)


# --- СБРОС ДАННЫХ ---

@router.callback_query(F.data == "admin_reset_data_confirm", IsAdmin())
async def admin_reset_data_confirm(callback: CallbackQuery):
    text = """🚨 ВНИМАНИЕ! 🚨

Вы уверены, что хотите сбросить ВСЕ пользовательские данные? Это действие необратимо и приведет к:

- Обнулению балансов (включая замороженные) у ВСЕХ пользователей.
- Удалению ВСЕХ товаров с маркета.
- Удалению ВСЕХ активных и завершенных сделок.

Пожалуйста, подтвердите свое намерение."""
    await callback.message.edit_text(text, reply_markup=get_admin_reset_confirmation_keyboard())
    await callback.answer()


@router.callback_query(F.data == "admin_reset_data_execute", IsAdmin())
async def admin_reset_data_execute(callback: CallbackQuery):
    if reset_all_user_data():
        text = "✅ Все пользовательские данные были успешно сброшены."
    else:
        text = "❌ Произошла ошибка при сбросе данных. Проверьте логи."
    
    await callback.message.edit_text(text, reply_markup=get_back_to_admin_menu_keyboard())
    await callback.answer("Операция завершена.", show_alert=True)
