import os
import logging
import datetime
import yt_dlp
from pytube import YouTube
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Required Bot Credentials
API_ID = int(os.getenv("API_ID", "22141398"))
API_HASH = os.getenv("API_HASH", "0c8f8bd171e05e42d6f6e5a6f4305389")
BOT_TOKEN = os.getenv("BOT_TOKEN", "8105194942:AAFzL74g4y3EMJdouoVUtRig4SP_1eZk_xs")

# Enable logging
logging.basicConfig(level=logging.INFO)

# Initialize bot
app = Client("YouTubeDownloader", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Custom start message
@app.on_message(filters.command("start"))
async def start(client, message):
    user_name = message.from_user.first_name
    user_id = message.from_user.id
    current_time = datetime.datetime.now().strftime("%H:%M %p")

    start_text = f"""
ʜᴇʏ {user_name}, `{user_id}`, Good welcome as `{current_time}` 🌤️ 👋  

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


# Fetch available qualities
@app.on_message(filters.text & filters.regex(r"https?://(www\.)?youtube\.com/watch\?v="))
async def fetch_qualities(client, message):
    url = message.text
    try:
        yt = YouTube(url)
        streams = yt.streams.filter(progressive=True, file_extension="mp4").order_by("resolution").desc()

        buttons = []
        for stream in streams:
            res = stream.resolution
            btn_text = f"{res} 📽️"
            buttons.append([InlineKeyboardButton(btn_text, callback_data=f"pytube_{stream.itag}")])

        # Add audio-only option
        audio_stream = yt.streams.filter(only_audio=True).first()
        buttons.append([InlineKeyboardButton("🔊 Audio Only", callback_data=f"pytube_{audio_stream.itag}")])

        # If `pytube` fails, add `yt-dlp` as backup
        buttons.append([InlineKeyboardButton("🔄 Try Alternative (yt-dlp)", callback_data="ytdlp")])

        keyboard = InlineKeyboardMarkup(buttons)
        await message.reply_text(f"🎬 **{yt.title}**\n\nSelect a quality:", reply_markup=keyboard)

    except Exception as e:
        await message.reply_text(f"⚠️ `pytube` failed: {str(e)}\n\n🔄 Switching to `yt-dlp`...")
        await fetch_qualities_ytdlp(client, message)


# Download using `pytube`
@app.on_callback_query(filters.regex(r"pytube_\d+"))
async def download_pytube(client, callback_query):
    itag = int(callback_query.data.split("_")[1])
    url = callback_query.message.reply_to_message.text
    try:
        yt = YouTube(url)
        stream = yt.streams.get_by_itag(itag)
        file_path = stream.download()

        await callback_query.message.reply_text("📥 Downloading... Please wait.")

        # Send file to user
        await callback_query.message.reply_video(video=file_path, caption="✅ Download Complete!")

        # Remove file after sending
        os.remove(file_path)

    except Exception as e:
        await callback_query.message.reply_text(f"❌ `pytube` failed: {str(e)}\n\n🔄 Trying `yt-dlp`...")
        await download_ytdlp(client, callback_query)


# Fetch available qualities using `yt-dlp`
async def fetch_qualities_ytdlp(client, message):
    url = message.text
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

        # Add audio-only option
        buttons.append([InlineKeyboardButton("🔊 Audio Only", callback_data="ytdlp_audio")])

        keyboard = InlineKeyboardMarkup(buttons)
        await message.reply_text(f"🎬 **{info.get('title')}**\n\nSelect a quality:", reply_markup=keyboard)

    except Exception as e:
        await message.reply_text(f"❌ `yt-dlp` failed: {str(e)}")


# Download using `yt-dlp`
@app.on_callback_query(filters.regex(r"ytdlp_"))
async def download_ytdlp(client, callback_query):
    format_id = callback_query.data.split("_")[1]
    url = callback_query.message.reply_to_message.text
    file_path = None

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

        # Send file to user
        if format_id == "audio":
            await callback_query.message.reply_audio(audio=file_path, caption="✅ Download Complete!")
        else:
            await callback_query.message.reply_video(video=file_path, caption="✅ Download Complete!")

        # Remove file after sending
        os.remove(file_path)

    except Exception as e:
        await callback_query.message.reply_text(f"❌ `yt-dlp` failed: {str(e)}")


if __name__ == "__main__":
    app.run()
