import os

# ============================================
# BOT CONFIGURATION - .env se load hoga
# ============================================
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "6517309435").split(",")]

# Points Settings (Admin panel se change kar sakta hai)
DEFAULT_POINTS_PER_REFERRAL = 10

# Redeem Settings
REDEEM_OPTIONS = [
    {"points": 100, "amount": 10, "label": "₹10"},
    {"points": 500, "amount": 50, "label": "₹50"},
    {"points": 1000, "amount": 100, "label": "₹100"},
    {"points": 2000, "amount": 200, "label": "₹200"},
    {"points": 5000, "amount": 500, "label": "₹500"},
]

# Bot Info
BOT_USERNAME = os.getenv("BOT_USERNAME", "YourBot")
DATABASE_PATH = "bot_database.db"
