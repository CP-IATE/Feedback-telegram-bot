"""
services.py — бізнес-логіка спільна для кількох хендлерів.
"""

import asyncio
from aiogram import Bot

import config as cfg
import dataBase as db
import interface as kb

#  ТОПІКИ 

async def create_verification_topic(bot: Bot, user_id: int, full_name: str) -> int | None:
    """Створює топік верифікації. Повертає thread_id або None."""
    try:
        topic = await bot.create_forum_topic(cfg.ADMIN_GROUP_ID, kb.TEXTS["topic_verification"].format(name=full_name[:20]))
        cfg.user_to_thread[user_id] = topic.message_thread_id
        return topic.message_thread_id
    except Exception as e:
        print(f"[services] Помилка створення топіку верифікації: {e}")
        return None

async def create_support_topic(bot: Bot, user_id: int, full_name: str) -> int | None:
    """Створює топік підтримки для підтвердженого студента. Повертає thread_id або None."""
    try:
        topic = await bot.create_forum_topic(cfg.ADMIN_GROUP_ID, kb.TEXTS["topic_support"].format(name=full_name[:20]))
        thread_id = topic.message_thread_id
        db.set_thread(user_id, thread_id)
        cfg.user_to_thread[user_id] = thread_id
        await bot.send_message(
            cfg.ADMIN_GROUP_ID,
            kb.TEXTS["admin_topic_created"].format(name=full_name),
            message_thread_id=thread_id,
            reply_markup=kb.get_topic_admin_kb(user_id)
        )
        return thread_id
    except Exception as e:
        print(f"[services] Помилка створення топіку підтримки: {e}")
        return None

async def delete_topic(bot: Bot, thread_id: int) -> None:
    try:
        await bot.delete_forum_topic(chat_id=cfg.ADMIN_GROUP_ID, message_thread_id=thread_id)
    except Exception as e:
        print(f"[services] Помилка видалення топіку: {e}")

#  ПІДТВЕРДЖЕННЯ / ВІДХИЛЕННЯ 

async def approve_student(bot: Bot, user_id: int, thread_id: int, full_name: str) -> None:
    """Підтверджує студента: перший запис в БД + повідомлення юзеру."""
    db.confirm_student(user_id, thread_id, full_name)
    cfg.user_to_thread[user_id] = thread_id
    try:
        await bot.send_message(user_id, kb.TEXTS["verify_success"])
    except Exception:
        pass

async def reject_student(bot: Bot, user_id: int, thread_id: int, reason_text: str) -> None:
    """Відхиляє студента: скидає БД, повідомляє, видаляє топік."""
    db.reset_student(user_id)
    cfg.user_to_thread.pop(user_id, None)
    try:
        await bot.send_message(user_id, kb.TEXTS["verify_rejected"].format(reason=reason_text))
    except Exception:
        pass
    await asyncio.sleep(3)
    await delete_topic(bot, thread_id)

#  ЗАКРИТТЯ ЧАТУ 

async def close_chat(bot: Bot, user_id: int, thread_id: int) -> None:
    """Закриває чат підтримки: обнуляє group_id, видаляє топік."""
    db.clear_thread(user_id)
    cfg.user_to_thread.pop(user_id, None)
    try:
        await bot.send_message(user_id, kb.TEXTS["chat_closed"])
    except Exception:
        pass
    await delete_topic(bot, thread_id)
