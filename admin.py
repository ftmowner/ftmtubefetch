from pyrogram import Client, filters
from pyrogram.types import Message
from database import add_admin, remove_admin, get_admins
from ftmconfig import OWNER_ID, DEFAULT_ADMINS

# Command: /add_admin user_id (Only Owner)
@Client.on_message(filters.command("add_admin") & filters.user(OWNER_ID))
async def add_admin_cmd(client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("❌ Usage: `/add_admin user_id`")
        return

    user_id = int(message.command[1])
    add_admin(user_id)

    await message.reply_text(f"✅ User `{user_id}` is now an Admin.")

# Command: /remove_admin user_id (Only Owner)
@Client.on_message(filters.command("remove_admin") & filters.user(OWNER_ID))
async def remove_admin_cmd(client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("❌ Usage: `/remove_admin user_id`")
        return

    user_id = int(message.command[1])
    if user_id in DEFAULT_ADMINS:
        await message.reply_text("❌ You cannot remove a Default Admin.")
        return

    if remove_admin(user_id):
        await message.reply_text(f"✅ User `{user_id}` is no longer an Admin.")
    else:
        await message.reply_text("⚠️ Failed to remove Admin.")

# Command: /admins (Shows List of Admins)
@Client.on_message(filters.command("admins"))
async def list_admins(client, message: Message):
    admin_list = get_admins()
    if not admin_list:
        await message.reply_text("⚠️ No admins found.")
        return

    admin_text = "👑 **List of Admins:**\n" + "\n".join([f"🔹 `{admin}`" for admin in admin_list])
    await message.reply_text(admin_text)
