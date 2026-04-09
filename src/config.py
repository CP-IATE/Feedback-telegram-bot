import os

# INFO: bot related token and group id for control
TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_GROUP_ID = int(os.getenv("ADMIN_GROUP_ID", 0))

# INFO: bot pass for access
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "kpi_power_2026")

user_to_thread: dict = {}
blacklist: set[int] = set()