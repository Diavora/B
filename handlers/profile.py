# handlers/profile.py

from aiogram import Router, F, types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from keyboards.inline import (
    get_profile_keyboard, get_my_deals_keyboard, get_deal_history_keyboard, 
    get_deal_details_keyboard, get_cancel_keyboard,
    get_withdraw_country_keyboard, get_withdraw_bank_keyboard, get_withdraw_confirmation_keyboard,
    get_country_keyboard, get_bank_keyboard, get_payment_confirmation_keyboard, get_back_to_profile_keyboard
)
from utils import db
from utils.db import update_deal_status, get_deal_info, add_balance, get_user_balance, get_user_deal_stats
from states import TopUpState, WithdrawState
from config import ADMIN_IDS, PAYMENT_SYSTEMS

router = Router()


def get_deal_text(deal_info, current_user_id):
    status_map = {
        'in_progress': 'В процессе',
        'item_sent': 'Ожидает подтверждения от покупателя',
        'completed': 'Завершена',
        'cancelled': 'Отменена',
        'in_dispute': 'Открыт спор'
    }

    # Определяем роль текущего пользователя
    if current_user_id == deal_info['buyer_id']:
        role = "Покупатель"
        partner_username = deal_info['seller_username']
    else:
        role = "Продавец"
        partner_username = deal_info['buyer_username']

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

# --- ХЕНДЛЕРЫ ПРОФИЛЯ ---

@router.message(F.text == "/profile")
async def profile_handler(message: Message):
    user_id = message.from_user.id
    profile_data = db.get_user_profile(user_id)
    deal_stats = db.get_user_deal_stats(user_id)

    if profile_data and deal_stats is not None:
        # Форматируем дату регистрации
        reg_date = profile_data['registration_date'].split(' ')[0]

        text = (
            f"<b>⚜️ Ваш профиль ⚜️</b>\n\n"
            f"🆔 <b>ID пользователя:</b> <code>{profile_data['user_id']}</code>\n"
            f"👤 <b>Никнейм:</b> @{profile_data['username']}\n\n"
            f"--- Финансы ---\n"
            f"💰 <b>Баланс:</b> {profile_data['balance']:.2f} RUB\n"
            f"❄️ <b>Заморожено:</b> {profile_data['frozen_balance']:.2f} RUB\n\n"
            f"--- Статистика ---\n"
            f"✅ <b>Успешных сделок:</b> {deal_stats['completed_deals']}\n"
            f"📅 <b>Дата регистрации:</b> {reg_date}"
        )
    else:
        text = "Не удалось загрузить данные профиля."
    await message.answer(text, reply_markup=get_profile_keyboard(), parse_mode="HTML")

@router.callback_query(F.data == "profile")
async def profile_callback_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    profile_data = db.get_user_profile(user_id)
    deal_stats = db.get_user_deal_stats(user_id)

    if profile_data and deal_stats is not None:
        # Форматируем дату регистрации
        reg_date = profile_data['registration_date'].split(' ')[0]

        text = (
            f"<b>⚜️ Ваш профиль ⚜️</b>\n\n"
            f"🆔 <b>ID пользователя:</b> <code>{profile_data['user_id']}</code>\n"
            f"👤 <b>Никнейм:</b> @{profile_data['username']}\n\n"
            f"--- Финансы ---\n"
            f"💰 <b>Баланс:</b> {profile_data['balance']:.2f} RUB\n"
            f"❄️ <b>Заморожено:</b> {profile_data['frozen_balance']:.2f} RUB\n\n"
            f"--- Статистика ---\n"
            f"✅ <b>Успешных сделок:</b> {deal_stats['completed_deals']}\n"
            f"📅 <b>Дата регистрации:</b> {reg_date}"
        )
    else:
        text = "Не удалось загрузить данные профиля."

    await callback.message.edit_text(text, reply_markup=get_profile_keyboard(user_id), parse_mode="HTML")
    await callback.answer()

# --- ПРОЦЕСС ПОПОЛНЕНИЯ БАЛАНСА ---

@router.callback_query(F.data == "top_up_balance")
async def top_up_balance_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(TopUpState.choosing_country)
    await callback.message.edit_text(
        "<b>💵 Пополнение баланса</b>\n\nВыберите страну для пополнения:",
        reply_markup=get_country_keyboard(PAYMENT_SYSTEMS),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(TopUpState.choosing_country, F.data.startswith("deposit_country_"))
async def deposit_country_chosen_handler(callback: CallbackQuery, state: FSMContext):
    country_code = callback.data.split("_")[2]
    await state.update_data(country_code=country_code)
    await state.set_state(TopUpState.choosing_bank)
    
    country_name = PAYMENT_SYSTEMS[country_code]['name']
    banks = PAYMENT_SYSTEMS[country_code]['banks']
    await callback.message.edit_text(
        f"<b>Выбрана страна:</b> {country_name}\n\nТеперь выберите банк:",
        reply_markup=get_bank_keyboard(country_code, banks),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(TopUpState.choosing_bank, F.data.startswith("deposit_bank_"))
async def deposit_bank_chosen_handler(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    country_code = parts[2]
    bank_code = parts[3]
    await state.update_data(bank_code=bank_code)
    await state.set_state(TopUpState.entering_amount)

    bank_name = PAYMENT_SYSTEMS[country_code]['banks'][bank_code]['name']
    currency = PAYMENT_SYSTEMS[country_code]['currency']
    
    await callback.message.edit_text(
        f"🏦 <b>Банк:</b> {bank_name}\n\n"
        f"Теперь, пожалуйста, введите сумму, на которую хотите пополнить баланс.\n\n"
        f"➡️ <b>Сумма в {currency}:</b>",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(TopUpState.entering_amount)
async def deposit_amount_entered_handler(message: Message, state: FSMContext):
    try:
        amount = float(message.text.replace(',', '.'))
        if amount <= 0:
            await message.answer("❌ Сумма должна быть положительной. Попробуйте еще раз.", reply_markup=get_cancel_keyboard())
            return
        await state.update_data(amount=amount)
    except (ValueError, TypeError):
        await message.answer("❌ Введено неверное значение. Пожалуйста, введите число.", reply_markup=get_cancel_keyboard())
        return

    data = await state.get_data()
    country_code = data['country_code']
    bank_code = data['bank_code']
    
    bank_info = PAYMENT_SYSTEMS[country_code]['banks'][bank_code]
    requisites = bank_info['requisites']
    bank_name = bank_info['name']
    currency = PAYMENT_SYSTEMS[country_code]['currency']

    text = (
        f"<b>Пожалуйста, совершите перевод по реквизитам ниже.</b>\n\n"
        f"➖➖➖➖➖➖➖➖➖➖➖➖\n"
        f"<b>Банк получателя:</b> {bank_name}\n"
        f"<b>Номер карты:</b> <code>{requisites}</code>\n"
        f"<b>Сумма к оплате:</b> <code>{amount:.2f} {currency}</code>\n"
        f"➖➖➖➖➖➖➖➖➖➖➖➖\n\n"
        f"⚠️ <b>Важно:</b> Убедитесь, что переводите точную сумму. После успешного перевода, нажмите кнопку «✅ Я оплатил»."
    )
    
    await state.set_state(TopUpState.confirming_payment)
    await message.answer(text, reply_markup=get_payment_confirmation_keyboard(country_code, bank_code), parse_mode="HTML")

@router.callback_query(TopUpState.confirming_payment, F.data == "check_payment")
async def check_payment_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "❌ <b>Оплата не найдена</b>\n\n"
        "К сожалению, мы не смогли найти ваш платеж. "
        "Пожалуйста, убедитесь, что вы перевели точную сумму и попробуйте снова через несколько минут.\n\n"
        "Если проблема не решится, обратитесь в службу поддержки.",
        reply_markup=get_back_to_profile_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

# --- ХЕНДЛЕРЫ СДЕЛОК ---

@router.callback_query(F.data == "my_deals")
async def my_deals_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    # Получаем только активные сделки
    deals = db.get_user_deals(user_id, status=('in_progress', 'item_sent', 'in_dispute'))
    await callback.message.edit_text(
        "<b>🤝 Ваши текущие сделки:</b>",
        reply_markup=get_my_deals_keyboard(deals),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "deal_history")
async def deal_history_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    # Получаем завершенные и отмененные сделки
    deals = db.get_user_deals(user_id, status=('completed', 'cancelled'))
    await callback.message.edit_text(
        "<b>📜 История ваших сделок:</b>",
        reply_markup=get_deal_history_keyboard(deals),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("deal_details_"))
async def deal_details_handler(callback: CallbackQuery):
    try:
        deal_id = int(callback.data.split("_")[2])
    except (ValueError, IndexError):
        await callback.answer("Ошибка: Неверный ID сделки.", show_alert=True)
        return

    user_id = callback.from_user.id
    result = db.get_deal_info(deal_id)

    if result['status'] != 'success':
        await callback.message.edit_text("Сделка не найдена!", reply_markup=get_back_to_profile_keyboard())
        await callback.answer()
        return

    deal_info = result['data']
    # Проверяем, является ли пользователь участником сделки
    if user_id not in [deal_info['buyer_id'], deal_info['seller_id']]:
        await callback.answer("Вы не являетесь участником этой сделки.", show_alert=True)
        return

    text = get_deal_text(deal_info, user_id)
    keyboard = get_deal_details_keyboard(deal_info, user_id)
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


# --- ДЕЙСТВИЯ В СДЕЛКЕ ---

async def update_deal_message(callback: CallbackQuery, deal_info: dict):
    """Вспомогательная функция для обновления сообщения о сделке."""
    user_id = callback.from_user.id
    text = get_deal_text(deal_info, user_id)
    keyboard = get_deal_details_keyboard(deal_info, user_id)
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")

@router.callback_query(F.data.startswith("deal_action_sent_"))
async def item_sent_handler(callback: CallbackQuery, bot: Bot):
    deal_id = int(callback.data.split('_')[3])
    user_id = callback.from_user.id

    result = db.update_deal_status(deal_id, 'item_sent', user_id)

    if result['status'] == 'success':
        deal_info = result['data']
        await update_deal_message(callback, deal_info)
        await callback.answer("✅ Статус сделки обновлен. Покупатель уведомлен.")
        try:
            await bot.send_message(
                deal_info['buyer_id'],
                f"Продавец по сделке #{deal_id} отметил, что передал товар. Пожалуйста, подтвердите получение."
            )
        except Exception as e:
            print(f"Ошибка при отправке уведомления покупателю {deal_info['buyer_id']}: {e}")
    elif result['status'] == 'not_seller':
        await callback.answer("❗️ Только продавец может выполнить это действие.", show_alert=True)
    elif result['status'] == 'wrong_status':
        await callback.answer("❗️ Неверный статус сделки для этого действия.", show_alert=True)
    else:
        await callback.answer("❗️ Произошла ошибка.", show_alert=True)

@router.callback_query(F.data.startswith("deal_action_confirm_"))
async def confirm_deal_handler(callback: CallbackQuery, bot: Bot):
    deal_id = int(callback.data.split('_')[3])
    user_id = callback.from_user.id

    result = db.complete_deal(deal_id, user_id)

    if result['status'] == 'success':
        deal_info = result['data']
        await update_deal_message(callback, deal_info)
        await callback.answer("✅ Сделка успешно завершена!")
        try:
            await bot.send_message(
                deal_info['seller_id'],
                f"Покупатель подтвердил получение товара по сделке #{deal_id}. Средства зачислены на ваш баланс."
            )
        except Exception as e:
            print(f"Ошибка при отправке уведомления продавцу {deal_info['seller_id']}: {e}")
    elif result['status'] == 'not_buyer':
        await callback.answer("❗️ Только покупатель может выполнить это действие.", show_alert=True)
    elif result['status'] == 'wrong_status':
        await callback.answer("❗️ Подтвердить получение можно только после отправки товара.", show_alert=True)
    else:
        await callback.answer("❗️ Произошла ошибка.", show_alert=True)

@router.callback_query(F.data.startswith("deal_action_cancel_"))
async def cancel_deal_handler(callback: CallbackQuery, bot: Bot):
    deal_id = int(callback.data.split('_')[3])
    user_id = callback.from_user.id

    result = db.cancel_deal(deal_id, user_id)

    if result['status'] == 'success':
        deal_info = result['data']
        await update_deal_message(callback, deal_info)
        await callback.answer("❌ Сделка отменена.")
        
        other_participant_id = deal_info['buyer_id'] if user_id == deal_info['seller_id'] else deal_info['seller_id']
        try:
            await bot.send_message(other_participant_id, f"Ваш партнер по сделке #{deal_id} отменил её.")
        except Exception as e:
            print(f"Не удалось уведомить второго участника об отмене сделки {deal_id}: {e}")

    elif result['status'] == 'not_participant':
        await callback.answer("❗️ Вы не участник этой сделки.", show_alert=True)
    elif result['status'] == 'already_finalized':
        await callback.answer("❗️ Эту сделку уже нельзя отменить.", show_alert=True)
    else:
        await callback.answer("❗️ Произошла ошибка.", show_alert=True)

@router.callback_query(F.data.startswith("deal_action_dispute_"))
async def open_dispute_handler(callback: CallbackQuery, bot: Bot):
    deal_id = int(callback.data.split('_')[3])
    user_id = callback.from_user.id

    result = db.open_dispute(deal_id, user_id)

    if result['status'] == 'success':
        deal_info = result['data']
        await update_deal_message(callback, deal_info)
        await callback.answer("❗️ Спор открыт. Администратор уведомлен.")

        # Уведомление администраторам и второму участнику
        other_participant_id = deal_info['buyer_id'] if user_id == deal_info['seller_id'] else deal_info['seller_id']
        admin_ids = ADMIN_IDS 
        
        try:
            await bot.send_message(other_participant_id, f"❗️ Ваш партнер по сделке #{deal_id} открыл спор. Ожидайте решения администрации.")
        except Exception as e:
            print(f"Не удалось уведомить второго участника о споре: {e}")

        for admin_id in admin_ids:
            try:
                await bot.send_message(admin_id, f"❗️ Открыт спор по сделке #{deal_id}. Требуется ваше вмешательство.")
            except Exception as e:
                print(f"Не удалось уведомить администратора {admin_id} о споре: {e}")

    elif result['status'] == 'not_participant':
        await callback.answer("❗️ Вы не участник этой сделки.", show_alert=True)
    elif result['status'] == 'already_finalized':
        await callback.answer("❗️ Спор по этой сделке уже нельзя открыть.", show_alert=True)
    else:
        await callback.answer("❗️ Произошла ошибка.", show_alert=True)


# --- ПРОЦЕСС ВЫВОДА СРЕДСТВ ---

@router.callback_query(F.data == "withdraw_balance")
async def withdraw_balance_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(WithdrawState.choosing_country)
    await callback.message.edit_text(
        "<b>📤 Вывод средств</b>\n\nВыберите страну для вывода:",
        reply_markup=get_withdraw_country_keyboard(PAYMENT_SYSTEMS),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(WithdrawState.choosing_country, F.data.startswith("withdraw_country_"))
async def withdraw_country_chosen_handler(callback: CallbackQuery, state: FSMContext):
    country_code = callback.data.split("_")[2]
    await state.update_data(country_code=country_code)
    await state.set_state(WithdrawState.choosing_bank)
    
    country_name = PAYMENT_SYSTEMS[country_code]['name']
    banks = PAYMENT_SYSTEMS[country_code]['banks']
    await callback.message.edit_text(
        f"<b>Выбрана страна:</b> {country_name}\n\nТеперь выберите банк для получения средств:",
        reply_markup=get_withdraw_bank_keyboard(country_code, banks),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(WithdrawState.choosing_bank, F.data.startswith("withdraw_bank_"))
async def withdraw_bank_chosen_handler(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    country_code = parts[2]
    bank_code = parts[3]
    await state.update_data(bank_code=bank_code)
    await state.set_state(WithdrawState.entering_amount)

    profile_data = db.get_user_profile(callback.from_user.id)
    balance = profile_data.get('balance', 0)
    bank_name = PAYMENT_SYSTEMS[country_code]['banks'][bank_code]
    currency = PAYMENT_SYSTEMS[country_code]['currency']
    
    await callback.message.edit_text(
        f"<b>Выбран банк:</b> {bank_name}\n"
        f"<b>Ваш баланс:</b> <code>{balance:.2f} RUB</code>\n\n"
        f"Введите сумму для вывода в <b>{currency}</b>.",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(WithdrawState.entering_amount)
async def withdraw_amount_entered_handler(message: Message, state: FSMContext):
    profile_data = db.get_user_profile(message.from_user.id)
    balance = profile_data.get('balance', 0)

    try:
        amount = float(message.text.replace(',', '.'))
        if amount <= 0:
            await message.answer("Сумма должна быть положительной.")
            return
        if amount > balance:
            await message.answer(f"Недостаточно средств. Ваш баланс: {balance:.2f} RUB")
            return
        await state.update_data(amount=amount)
    except (ValueError, TypeError):
        await message.answer("Пожалуйста, введите корректное число.")
        return

    await state.set_state(WithdrawState.entering_requisites)
    await message.answer("Теперь введите номер вашей карты или счета для зачисления средств.", reply_markup=get_cancel_keyboard())

@router.message(WithdrawState.entering_requisites)
async def requisites_entered_handler(message: Message, state: FSMContext):
    await state.update_data(requisites=message.text)
    data = await state.get_data()
    
    country_code = data['country_code']
    bank_code = data['bank_code']
    amount = data['amount']
    requisites = data['requisites']

    country_name = PAYMENT_SYSTEMS[country_code]['name']
    bank_name = PAYMENT_SYSTEMS[country_code]['banks'][bank_code]
    currency = PAYMENT_SYSTEMS[country_code]['currency']

    text = (
        f"<b>Подтвердите заявку на вывод</b>\n\n"
        f"<b>Сумма:</b> <code>{amount:.2f} {currency}</code>\n"
        f"<b>Страна:</b> {country_name}\n"
        f"<b>Банк:</b> {bank_name}\n"
        f"<b>Реквизиты:</b> <code>{requisites}</code>\n\n"
        f"Пожалуйста, внимательно проверьте все данные. После подтверждения, отменить операцию будет невозможно."
    )

    await state.set_state(WithdrawState.confirming_withdrawal)
    await message.answer(text, reply_markup=get_withdraw_confirmation_keyboard(), parse_mode="HTML")

@router.callback_query(WithdrawState.confirming_withdrawal, F.data == "confirm_withdrawal")
async def confirm_withdrawal_handler(callback: CallbackQuery, state: FSMContext):
    # Здесь должна быть логика списания баланса и реальной отправки
    # Пока что это просто заглушка
    data = await state.get_data()
    amount = data.get('amount')
    # db.create_withdrawal_request(user_id=callback.from_user.id, data=data)
    await state.clear()
    await callback.message.edit_text(
        f"✅ <b>Заявка на вывод {amount:.2f} RUB успешно создана!</b>\n\n"
        "Средства поступят на ваши реквизиты в течение 24 часов.",
        parse_mode="HTML",
        reply_markup=None
    )
    await callback.answer()

# Отмена любого состояния FSM
@router.callback_query(F.data == "cancel_fsm")
async def cancel_fsm_handler(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await callback.answer()
        return

    await state.clear()
    await callback.message.edit_text("Действие отменено.", reply_markup=None)
    # Можно вернуть в профиль для удобства
    await profile_callback_handler(callback) 
    await callback.answer()
