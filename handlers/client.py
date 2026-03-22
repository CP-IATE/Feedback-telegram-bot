from aiogram import Router
from aiogram.types import Message

import config as cfg
import dataBase as db
import interface as kb
import services

router = Router()

ALLOWED_CONTENT_TYPES = {"text", "photo", "document"}

def _content_type(message: Message) -> str:
    if message.text:       return "text"
    if message.photo:      return "photo"
    if message.document:   return "document"
    if message.voice:      return "voice"
    if message.video_note: return "video_note"
    if message.sticker:    return "sticker"
    if message.video:      return "video"
    if message.audio:      return "audio"
    if message.animation:  return "animation"
    return "unknown"

@router.message()
async def handle_client(message: Message):
    if message.chat.id == cfg.ADMIN_GROUP_ID:
        return

    user_id   = message.from_user.id
    full_name = message.from_user.full_name
    student   = db.get_student(user_id)

    is_confirmed = student["confirmed_student"] if student else 0
    thread_id    = student["group_id"]          if student else None

    #  ПІДТВЕРДЖЕНИЙ СТУДЕНТ 
    if is_confirmed == 1:
        if _content_type(message) not in ALLOWED_CONTENT_TYPES:
            await message.answer(kb.TEXTS["content_blocked"])
            return

        if not thread_id:
            thread_id = await services.create_support_topic(message.bot, user_id, full_name)
            if not thread_id:
                await message.answer(kb.TEXTS["topic_error"])
                return

        try:
            await message.copy_to(chat_id=cfg.ADMIN_GROUP_ID, message_thread_id=thread_id)
        except Exception:
            await message.answer(kb.TEXTS["send_error"])
        return

    #  ВЕРИФІКАЦІЯ: фото студентського 
    if message.photo:
        if user_id in cfg.user_to_thread:
            return

        thread_id = await services.create_verification_topic(message.bot, user_id, full_name)
        if not thread_id:
            await message.answer(kb.TEXTS["topic_error"])
            return

        await message.bot.send_photo(
            cfg.ADMIN_GROUP_ID,
            message.photo[-1].file_id,
            message_thread_id=thread_id,
            caption=kb.TEXTS["admin_new_student"].format(name=full_name, user_id=user_id),
            reply_markup=kb.get_validation_kb(user_id)
        )
        await message.answer(kb.TEXTS["wait_for_admin"])
        return

    #  НЕ ВЕРИФІКОВАНИЙ 
    if message.text == "/start":
        await message.answer(kb.TEXTS["start_unverified"])
    else:
        await message.answer(kb.TEXTS["not_verified"])
