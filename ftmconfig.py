import os

# ✅ MongoDB URI (From Environment Variable)
MONGO_URI = os.getenv("MONGO_URI", None)

if not MONGO_URI:
    raise ValueError("❌ MongoDB URI not found! Set `MONGO_URI` in environment variables.")

# ✅ Bot Credentials (From Environment Variables)
API_ID = int(os.getenv("API_ID", 22141398))
API_HASH = os.getenv("API_HASH", "0c8f8bd171e05e42d6f6e5a6f4305389")
BOT_TOKEN = os.getenv("BOT_TOKEN", "8105194942:AAFzL74g4y3EMJdouoVUtRig4SP_1eZk_xs")

# ✅ Owner & Admin Settings
OWNER_ID = int(os.getenv("OWNER_ID", 123456789))  # Replace with your Telegram User ID
DEFAULT_ADMINS = [OWNER_ID, 987654321]  # Replace with actual Admin IDs
