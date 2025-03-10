from pyrogram import Client, filters
from pyrogram.types import Message
from datetime import datetime, timedelta
from database import add_premium_user, remove_premium_user, get_plan, get_expiry, is_admin

# Command: /add_premium user_id plan_name days (Admins Only)
@Client.on_message(filters.command("add_premium"))
async def add_premium(client, message: Message):
    if not is_admin(client, message):  # Check if the sender is an admin
        await message.reply_text("❌ You are not authorized to add premium users.")
        return

    if len(message.command) < 4:
        await message.reply_text("❌ Usage: `/add_premium user_id plan_name days`")
        return

    user_id = int(message.command[1])
    plan_name = message.command[2]
    days = int(message.command[3])

    expiry_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
    add_premium_user(user_id, plan_name, expiry_date)

    await message.reply_text(f"✅ User `{user_id}` upgraded to **{plan_name}** until **{expiry_date}**.")

# Command: /remove_premium user_id (Admins Only)
@Client.on_message(filters.command("remove_premium"))
async def remove_premium(client, message: Message):
    if not is_admin(client, message):
        await message.reply_text("❌ You are not authorized to remove premium users.")
        return

    if len(message.command) < 2:
        await message.reply_text("❌ Usage: `/remove_premium user_id`")
        return

    user_id = int(message.command[1])
    remove_premium_user(user_id)

    await message.reply_text(f"✅ User `{user_id}` is no longer premium.")

# Command: /myplan (Any User)
@Client.on_message(filters.command("myplan"))
async def my_plan(client, message: Message):
    user_id = message.from_user.id
    plan = get_plan(user_id)
    expiry = get_expiry(user_id)

    await message.reply_text(f"🔹 **Your Plan:** {plan}\n🔹 **Expires On:** {expiry}")
