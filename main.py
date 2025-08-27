import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackContext,
    MessageHandler,
    CallbackQueryHandler,
    filters
)
from dotenv import load_dotenv

# ===============================
# 🔹 Load Token from .env
# ===============================
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ===============================
# 🔹 Global Config
# ===============================
SUPER_ADMIN = 6266487624   # Replace with your Telegram user ID
MUST_JOIN = [
    "https://t.me/boteratrack",
    "https://t.me/boterapro"
]

# Simple in-memory DB (replace with SQLite or Mongo later)
DB_FILE = "db.json"
if os.path.exists(DB_FILE):
    with open(DB_FILE, "r") as f:
        db = json.load(f)
else:
    db = {"users": {}, "mini_bots": {}}


def save_db():
    with open(DB_FILE, "w") as f:
        json.dump(db, f)


# ===============================
# 🔹 Must Join Check
# ===============================
async def check_membership(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    # NOTE: Ideally use bot.get_chat_member for real check
    # For now just simulate (since Render may not allow full admin perms)
    return True  # Stub → always true in this minimal working version


# ===============================
# 🔹 Start Command
# ===============================
async def start(update: Update, context: CallbackContext):
    user = update.effective_user
    user_id = str(user.id)

    if user_id not in db["users"]:
        db["users"][user_id] = {"balance": 0, "referrals": [], "is_mini_admin": False}
        save_db()

    # Must Join Check
    keyboard = [[InlineKeyboardButton("✅ Joined", callback_data="verify_join")]]
    links = "\n".join([f"➡️ {ch}" for ch in MUST_JOIN])
    await update.message.reply_text(
        f"👋 Welcome {user.first_name}!\n\n"
        f"To use this bot, you must join the following channels:\n{links}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def verify_join(update: Update, context: CallbackContext):
    query = update.callback_query
    user = query.from_user
    if await check_membership(update, context):
        await query.message.reply_text("✅ Access granted!\nUse /menu to continue.")
    else:
        await query.message.reply_text("❌ Please join all required channels first.")


# ===============================
# 🔹 Menu
# ===============================
async def menu(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("➕ Create Mini Bot", callback_data="create_bot")],
        [InlineKeyboardButton("💰 My Balance", callback_data="balance")],
        [InlineKeyboardButton("👥 Referrals", callback_data="referrals")]
    ]
    if update.effective_user.id == SUPER_ADMIN:
        keyboard.append([InlineKeyboardButton("🔐 Super Admin Panel", callback_data="super_admin")])
    await update.message.reply_text("📍 Main Menu", reply_markup=InlineKeyboardMarkup(keyboard))


# ===============================
# 🔹 Callback Queries
# ===============================
async def callbacks(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = str(query.from_user.id)

    if query.data == "create_bot":
        db["users"][user_id]["is_mini_admin"] = True
        db["mini_bots"][user_id] = {
            "name": f"{query.from_user.first_name}'s Bot",
            "users": [],
            "channels": [],
            "balance": 0,
            "referrals": []
        }
        save_db()
        await query.message.reply_text(
            f"✅ Mini Bot created!\nUse /mybot to manage your bot."
        )

    elif query.data == "balance":
        bal = db["users"][user_id]["balance"]
        await query.message.reply_text(f"💰 Your balance: ₦{bal}")

    elif query.data == "referrals":
        refs = db["users"][user_id]["referrals"]
        await query.message.reply_text(f"👥 You referred {len(refs)} users.")

    elif query.data == "super_admin":
        if query.from_user.id == SUPER_ADMIN:
            await query.message.reply_text("🔐 Super Admin Panel:\n/broadcast\n/stats")
        else:
            await query.message.reply_text("❌ Access denied.")


# ===============================
# 🔹 Mini Bot Panel
# ===============================
async def mybot(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    if user_id not in db["mini_bots"]:
        await update.message.reply_text("❌ You don't own a mini bot yet. Use /menu to create one.")
        return

    bot_data = db["mini_bots"][user_id]
    await update.message.reply_text(
        f"🤖 {bot_data['name']} Panel\n"
        f"👥 Users: {len(bot_data['users'])}\n"
        f"💰 Balance: ₦{bot_data['balance']}"
    )


# ===============================
# 🔹 Super Admin Commands
# ===============================
async def broadcast(update: Update, context: CallbackContext):
    if update.effective_user.id != SUPER_ADMIN:
        return
    text = " ".join(context.args)
    for uid in db["users"]:
        try:
            await context.bot.send_message(chat_id=int(uid), text=f"📢 Broadcast:\n{text}")
        except:
            pass
    await update.message.reply_text("✅ Broadcast sent.")


async def stats(update: Update, context: CallbackContext):
    if update.effective_user.id != SUPER_ADMIN:
        return
    total_users = len(db["users"])
    total_bots = len(db["mini_bots"])
    await update.message.reply_text(
        f"📊 Stats:\n👥 Users: {total_users}\n🤖 Mini Bots: {total_bots}"
    )


# ===============================
# 🔹 Main
# ===============================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CommandHandler("mybot", mybot))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("stats", stats))

    app.add_handler(CallbackQueryHandler(verify_join, pattern="verify_join"))
    app.add_handler(CallbackQueryHandler(callbacks))

    app.run_polling()


if __name__ == "__main__":
    main()