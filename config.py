import os

# ѕытаемс€ вз€ть из системы, если там пусто Ч ставим пустую строку или дефолт
TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_GROUP_ID = int(os.getenv("ADMIN_GROUP_ID", 0))

# Ёти параметры можно оставить в коде, если они не секретные
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "kpi_power_2026")

user_to_thread: dict = {}
blacklist: set[int] = set()