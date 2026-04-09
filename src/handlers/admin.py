import asyncio
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter

import config as cfg
import dataBase as db
import interface as kb
import services

router = Router()

class AdminStates(StatesGroup):
    waiting_custom_reason = State()

#  ticket_close (кнопка = /close) 

@router.callback_query(F.data.startswith("ticket_close_"))
async def ticket_close_handler(callback: CallbackQuery):
    user_id   = int(callback.data.split("_")[-1])
    thread_id = callback.message.message_thread_id

    await callback.answer()
    await callback.message.answer(kb.TEXTS["admin_close_pending"])
    await asyncio.sleep(3)
    await services.close_chat(callback.bot, user_id, thread_id)


# region BAN
#  ticket_delete (кнопка в топіку = бан) 
# TODO: кнопка на бан
#
#
#
# @router.callback_query(F.data.startswith("ticket_delete_"))
# async def ticket_delete_handler(callback: CallbackQuery):
#     user_id   = int(callback.data.split("_")[-1])
#     thread_id = callback.message.message_thread_id
#
#     cfg.blacklist.add(user_id)
#     db.reset_student(user_id)
#     cfg.user_to_thread.pop(user_id, None)
#
#     try:
#         await callback.bot.send_message(user_id, kb.TEXTS["banned"])
#     except Exception:
#         pass
#
#     await callback.answer(kb.TEXTS["admin_ticket_deleted"])
#     await services.delete_topic(callback.bot, thread_id)

#  /ban 
# TODO: Бан

# @router.message(F.chat.id == cfg.ADMIN_GROUP_ID, F.text.startswith("/ban"))
# async def ban_command(message: Message):
#     user_id = _parse_user_id(message)
#     if not user_id:
#         await message.reply(kb.TEXTS["admin_ban_usage"])
#         return
#
#     if user_id in cfg.blacklist:
#         await message.reply(kb.TEXTS["admin_already_banned"].format(user_id=user_id))
#         return
#
#     cfg.blacklist.add(user_id)
#     db.reset_student(user_id)
#     cfg.user_to_thread.pop(user_id, None)
#
#     try:
#         await message.bot.send_message(user_id, kb.TEXTS["banned"])
#     except Exception:
#         pass
#
#     await message.reply(kb.TEXTS["admin_banned"].format(user_id=user_id))

#  /unban 
# TODO: Розбан

# @router.message(F.chat.id == cfg.ADMIN_GROUP_ID, F.text.startswith("/unban"))
# async def unban_command(message: Message):
#     user_id = _parse_user_id(message)
#     if not user_id:
#         await message.reply(kb.TEXTS["admin_unban_usage"])
#         return
#
#     if user_id not in cfg.blacklist:
#         await message.reply(kb.TEXTS["admin_not_banned"].format(user_id=user_id))
#         return
#
#     cfg.blacklist.discard(user_id)
#
#     try:
#         await message.bot.send_message(user_id, kb.TEXTS["unbanned"])
#     except Exception:
#         pass
#
#     await message.reply(kb.TEXTS["admin_unbanned"].format(user_id=user_id))
# endregion 


#  /close або /done 

@router.message(F.chat.id == cfg.ADMIN_GROUP_ID, F.text.in_({"/close", "/done"}))
async def close_command(message: Message):
    if not message.message_thread_id:
        return

    user_id = db.get_user_by_thread(message.message_thread_id)
    if not user_id:
        await message.reply(kb.TEXTS["admin_no_user"])
        return

    await message.answer(kb.TEXTS["admin_close_pending"])
    await asyncio.sleep(3)
    await services.close_chat(message.bot, user_id, message.message_thread_id)

#  Підтвердження 

@router.callback_query(F.data.startswith("verify_accept_"))
async def approve_handler(callback: CallbackQuery):
    user_id   = int(callback.data.split("_")[-1])
    thread_id = callback.message.message_thread_id
    full_name = callback.message.caption.split("\n")[0].replace("Нова заявка: ", "").strip()

    await callback.answer(kb.TEXTS["cb_accepted"])
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(kb.TEXTS["admin_verified"])

    await services.approve_student(callback.bot, user_id, thread_id, full_name)

#  Відхилення: показати причини 

@router.callback_query(F.data.startswith("verify_reject_"))
async def reject_show_reasons(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[-1])
    await callback.message.edit_reply_markup(reply_markup=kb.get_rejection_reasons_kb(user_id))
    await callback.answer()

#  Вибір причини 

@router.callback_query(F.data.startswith("reason_"))
async def reject_reasons_handler(callback: CallbackQuery, state: FSMContext):
    parts      = callback.data.split("_")
    reason_key = parts[1]
    user_id    = int(parts[2])
    thread_id  = callback.message.message_thread_id

    if reason_key == "cancel":
        await callback.message.edit_reply_markup(reply_markup=kb.get_validation_kb(user_id))
        return await callback.answer()

    if reason_key == "custom":
        await state.update_data(target_id=user_id, thread_id=thread_id)
        await state.set_state(AdminStates.waiting_custom_reason)
        await callback.message.answer(kb.TEXTS["custom_reason_prompt"])
        return await callback.answer()

    reason_text = kb.REJECTION_REASONS.get(reason_key, "Некоректні дані")
    await callback.message.answer(kb.TEXTS["rejected_pending"].format(reason=reason_text))
    await callback.answer()

    await services.reject_student(callback.bot, user_id, thread_id, reason_text)

#  Своя причина: чекаємо текст 

@router.message(AdminStates.waiting_custom_reason, F.chat.id == cfg.ADMIN_GROUP_ID)
async def custom_reason_input(message: Message, state: FSMContext):
    data      = await state.get_data()
    user_id   = data["target_id"]
    thread_id = data["thread_id"]
    await state.clear()

    reason_text = message.text or "Без причини"
    await message.answer(kb.TEXTS["rejected_pending"].format(reason=reason_text))

    await services.reject_student(message.bot, user_id, thread_id, reason_text)

#  Пересилання адмін -> студент 

@router.message(F.chat.id == cfg.ADMIN_GROUP_ID, StateFilter(None))
async def admin_to_user_reply(message: Message):
    if not message.message_thread_id or message.from_user.is_bot:
        return
    if message.text and message.text.startswith("/"):
        return

    user_id = db.get_user_by_thread(message.message_thread_id)
    if user_id:
        try:
            await message.copy_to(chat_id=user_id)
        except Exception:
            await message.reply(kb.TEXTS["forward_error"])

#  Хелпер 

def _parse_user_id(message: Message) -> int | None:
    parts = (message.text or "").split()
    if len(parts) >= 2:
        try:
            return int(parts[1])
        except ValueError:
            return None
    if message.message_thread_id:
        return db.get_user_by_thread(message.message_thread_id)
    return None
