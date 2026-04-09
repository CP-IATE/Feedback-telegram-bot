from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

TEXTS = {
    "start_unverified": "Привіт! Для того, щоб користуватися ботом, потрібно пройти верифікацію.\n\nНадішліть чітке фото свого студентського квитка для перевірки.",
    "wait_for_admin": "Фото отримано! ⏳ Очікуйте на перевірку адміністратором.",
    "verify_success": "✅ Ваш студентський підтверджено! Тепер ви можете надсилати звернення.\n⚠️ Надсилати можна лише текст, фото або документи.",
    "verify_rejected": "❌ Ваш студентський відхилено.\nПричина: {reason}\n\nСпробуйте надіслати фото ще раз.",
    "user_menu": "Головне меню. Оберіть дію або просто напишіть повідомлення для звернення:",

    "admin_new_student": "📄 <b>Нова заявка на верифікацію!</b>\nСтудент: {name} (ID: {user_id})\nПеревірте фото студентського нижче.",
    "admin_help": "🔧 <b>Меню адміністратора</b>\nВиберіть необхідну дію:",
    "admin_topic_created": "Новий тікет від {name}. Всі повідомлення звідси будуть пересилатися студенту.",

    "chat_closed":          "✅ Адміністратор завершив діалог. Чат закрито.",
    "content_blocked":      "⚠️ Дозволено надсилати лише текст, фото або документи.",
    "not_verified":         "⚠️ Спочатку пройдіть верифікацію — надішліть фото студентського квитка.",
    "topic_error":          "❌ Помилка при створенні чату. Спробуйте ще раз.",
    "send_error":           "❌ Не вдалося відправити повідомлення.",
    "banned":               "🚫 Вас заблоковано. Зверніться до адміністратора.",
    "unbanned":             "✅ Вас розблоковано.\nНадішліть фото студентського квитка для верифікації.",
    "admin_verified":       "✅ Студента підтверджено. Чат відкритий. Закрийте через /close.",
    "admin_close_pending":  "⌛ Закриваю чат через 3 секунди...",
    "admin_no_user":        "❌ Юзера не знайдено для цього топіку.",
    "admin_banned":         "🚫 Юзер {user_id} доданий до чорного списку.",
    "admin_unbanned":       "✅ Юзер {user_id} видалений з чорного списку.",
    "admin_already_banned": "⚠️ Юзер {user_id} вже в чорному списку.",
    "admin_not_banned":     "⚠️ Юзер {user_id} не в чорному списку.",
    "admin_ban_usage":      "❌ Вкажіть ID: /ban 123456789",
    "admin_unban_usage":    "❌ Вкажіть ID: /unban 123456789",
    "admin_ticket_deleted": "🗑 Студента заблоковано і чат видалено.",
    "forward_error":        "⚠️ Не вдалося надіслати (можливо, бан).",
    "custom_reason_prompt": "✍️ Введіть причину відхилення:",
    "rejected_pending":     "🚫 Відхилено: {reason}. Видалення через 3 сек...",
    "cb_accepted":          "✅ Підтверджено",
    "topic_verification":   "🎫 {name}",
    "topic_support":        "💬 {name}",
}

REJECTION_REASONS = {
    "blur":   "Нечітке фото",
    "nodata": "Не видно ПІБ",
    "fake":   "Чужий документ",
    "expired" : "Документ вже не дійсний",
}

def get_user_main_kb():
    builder = ReplyKeyboardBuilder()
    builder.button(text="📝 Написати звернення")
    builder.button(text="ℹ️ Мій профіль")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

def get_cancel_kb():
    builder = ReplyKeyboardBuilder()
    builder.button(text="❌ Скасувати")
    return builder.as_markup(resize_keyboard=True)

def get_admin_main_kb():
    builder = ReplyKeyboardBuilder()
    builder.button(text="👥 Керування ролями")
    return builder.as_markup(resize_keyboard=True)

def get_validation_kb(user_id: int):
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Прийняти", callback_data=f"verify_accept_{user_id}")
    builder.button(text="❌ Відхилити", callback_data=f"verify_reject_{user_id}")
    builder.adjust(2)
    return builder.as_markup()

def get_rejection_reasons_kb(user_id: int):
    builder = InlineKeyboardBuilder()
    for key, text in REJECTION_REASONS.items():
        builder.button(text=text, callback_data=f"reason_{key}_{user_id}")
    builder.button(text="Написати свою причину", callback_data=f"reason_custom_{user_id}")
    builder.button(text="🔙 Назад", callback_data=f"reason_cancel_{user_id}")
    builder.adjust(1)
    return builder.as_markup()

def get_topic_admin_kb(user_id: int):
    builder = InlineKeyboardBuilder()
    builder.button(text="🔒 Закрити тікет", callback_data=f"ticket_close_{user_id}")
    builder.button(text="🗑 Видалити чат та скинути бота", callback_data=f"ticket_delete_{user_id}")
    builder.adjust(2)
    return builder.as_markup()
