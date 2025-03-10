import os
import logging
import datetime
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from premium import add_premium, remove_premium, my_plan
from admin import add_admin_cmd, remove_admin_cmd, list_admins
from database import is_admin, get_plan, get_expiry
from ftmconfig import API_ID, API_HASH, BOT_TOKEN, OWNER_ID

# Enable logging
logging.basicConfig(level=logging.INFO)

# Initialize bot
app = Client("ftmbotzx-ytdl", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Store links to prevent losing them
youtube_links = {}

# ✅ Custom start message
@app.on_message(filters.command("start"))
async def start(client, message):
    user_name = message.from_user.first_name
    user_id = message.from_user.id
    current_time = datetime.datetime.now().strftime("%H:%M %p")

    start_text = f"""
ʜᴇʏ {user_name}, `{user_id}`, Good welcome at `{current_time}` 🌤️ 👋  

ɪ ᴀᴍ ᴠᴇʀʏ ᴀɴᴅ ᴍᴏsᴛ ᴘᴏᴡᴇʀꜰᴜʟ 🎥 YᴏᴜTᴜʙᴇ ᴅᴏᴡɴʟᴏᴀᴅᴇʀ ʙᴏᴛ ɴᴀᴍᴇᴅ ᴀs ⚡ **ғᴛᴍ ᴛᴜʙᴇғᴇᴛᴄʜ** ᴛɪʟʟ ɴᴏᴡ ᴄʀᴇᴀᴛᴇᴅ ʙʏ **Fᴛᴍ Dᴇᴠᴇʟᴏᴘᴇʀᴢ** 🚀  
Opened at **{current_time}**  

🌿 **ᴍᴀɪɴᴛᴀɪɴᴇᴅ ʙʏ:** [Fᴛᴍ Dᴇᴠᴇʟᴏᴘᴇʀᴢ](https://t.me/ftmdeveloperz)
    """

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Updates", url="https://t.me/ftmbotzx")],
        [InlineKeyboardButton("💬 Support", url="https://t.me/ftmbotzx_support")],
        [InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/ftmdeveloperz")],
        [InlineKeyboardButton("👑 Owner", url="https://t.me/ftmdeveloperz")]
    ])

    await message.reply_text(start_text, reply_markup=keyboard, disable_web_page_preview=True)

# ✅ Command: /myplan (Check Subscription Plan)
@app.on_message(filters.command(["myplan", "my_plan"]))
async def my_plan(client, message: Message):
    user_id = message.from_user.id
    plan = get_plan(user_id)
    expiry = get_expiry(user_id)
    await message.reply_text(f"🔹 **Your Plan:** {plan}\n🔹 **Expires On:** {expiry}")

# ✅ Command: /id (Check Telegram User ID)
@app.on_message(filters.command("id"))
async def get_id(client, message: Message):
    user_id = message.from_user.id
    await message.reply_text(f"🆔 **Your Telegram ID:** `{user_id}`")

# ✅ Command: /info (Get Full Telegram Info)
@app.on_message(filters.command("info"))
async def get_info(client, message: Message):
    user = message.from_user
    info_text = f"""
👤 **Your Telegram Info**
🔹 **ID:** `{user.id}`
🔹 **Username:** @{user.username if user.username else "N/A"}
🔹 **First Name:** {user.first_name}
🔹 **Last Name:** {user.last_name if user.last_name else "N/A"}
🔹 **Language Code:** {user.language_code}
"""
    await message.reply_text(info_text)

# ✅ Fetch available qualities using `yt-dlp`
@app.on_message(filters.text & filters.regex(r"(https?:\/\/)?(www\.|m\.)?(youtube\.com|youtu\.?be)\/.+"))
async def fetch_qualities(client, message):
    url = message.text
    youtube_links[message.chat.id] = url  # Save the link
    print(f"Received YouTube link: {url}")  # Debugging

    try:
        ydl_opts = {"quiet": True, "cookiefile": "cookies.txt"}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get("formats", [])

        buttons = []
        for fmt in formats:
            if fmt.get("ext") == "mp4" and fmt.get("height"):
                res = f"{fmt.get('height')}p"
                buttons.append([InlineKeyboardButton(res, callback_data=f"ytdlp_{fmt['format_id']}")])

        buttons.append([InlineKeyboardButton("🔊 Audio Only", callback_data="ytdlp_audio")])

        keyboard = InlineKeyboardMarkup(buttons)
        await message.reply_text(f"🎬 **{info.get('title')}**\n\nSelect a quality:", reply_markup=keyboard)

    except Exception as e:
        await message.reply_text(f"❌ `yt-dlp` failed: {str(e)}")

# ✅ Download using `yt-dlp`
@app.on_callback_query(filters.regex(r"ytdlp_"))
async def download_ytdlp(client, callback_query):
    format_id = callback_query.data.split("_")[1]
    chat_id = callback_query.message.chat.id
    url = youtube_links.get(chat_id)  # Retrieve stored link
    
    if not url:
        await callback_query.message.reply_text("❌ Error: Unable to find the original YouTube link.")
        return

    try:
        ydl_opts = {
            "format": format_id if format_id != "audio" else "bestaudio",
            "outtmpl": "%(title)s.%(ext)s",
            "quiet": True,
            "cookiefile": "cookies.txt",
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        await callback_query.message.reply_text("📥 Downloading... Please wait.")
        await callback_query.message.reply_video(video=file_path, caption="✅ Download Complete!")
        os.remove(file_path)

    except Exception as e:
        await callback_query.message.reply_text(f"❌ `yt-dlp` failed: {str(e)}")

# ✅ Start Bot
if __name__ == "__main__":
    print("🚀 Bot is starting...")
    app.run()
