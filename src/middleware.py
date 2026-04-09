"""
middleware.py — захист від спаму та зловживань.

ThrottlingMiddleware  — обмежує частоту повідомлень від одного юзера.
BlacklistMiddleware   — блокує юзерів зі списку (закоментовано, буде додано з постійним баном в БД).
"""

import time
from collections import defaultdict
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

import config as cfg


class ThrottlingMiddleware(BaseMiddleware):
    """
    Пропускає не більше одного повідомлення на `rate_limit` секунд від юзера.
    При перевищенні — відповідає попередженням і скидає хендлер.
    Повідомлення з групи адміна не обмежуються.
    """

    def __init__(self, rate_limit: float = 1.5) -> None:
        self.rate_limit = rate_limit
        self._last_seen: dict[int, float] = defaultdict(float)
        self._warned: dict[int, float] = defaultdict(float)

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any],
    ) -> Any:
        if event.chat.id == cfg.ADMIN_GROUP_ID:
            return await handler(event, data)

        user_id = event.from_user.id
        now = time.monotonic()
        delta = now - self._last_seen[user_id]

        if delta < self.rate_limit:
            if now - self._warned[user_id] > 5:
                self._warned[user_id] = now
                await event.answer("⚠️ Не так швидко. Зачекайте трохи.")
            return

        self._last_seen[user_id] = now
        return await handler(event, data)


# region BAN
# TODO: Блекліст ?
# class BlacklistMiddleware(BaseMiddleware):
#     async def __call__(
#         self,
#         handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
#         event: TelegramObject,
#         data: dict[str, Any],
#     ) -> Any:
#         if isinstance(event, Message):
#             if event.from_user and event.from_user.id in cfg.blacklist:
#                 return
#         return await handler(event, data)
# endregion 