import os
import json
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters
import threading

# -------------------------------
# Bot Token (your main bot)
# -------------------------------
TOKEN = "8263358249:AAFhhObsLAepIqNJGrPG_-DYN6TwsscB5Lo"

DATA_FILE = "users.json"

# Channels all participants must join
REQUIRED_CHANNELS = ["@boteratrack", "@boterapro"]

# -------------------------------
# Logging
# -------------------------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# -------------------------------
# Load/save users
# -------------------------------
def load_users():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(DATA_FILE, "w") as f:
        json.dump(users, f, indent=2)

# -------------------------------
# Participant verification
# -------------------------------
async def check_membership(bot, user_id):
    for channel in REQUIRED_CHANNELS:
        try:
            member = await bot.get_chat_member(channel, user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True

# -------------------------------
# Bot creation states
# -------------------------------
CHOOSING_THEME = 1

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome! To create your mini-bot, just choose a design/theme.\n"
        "Send /create to start."
    )

async def create(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    users = load_users()
    if not await check_membership(update.message.bot, update.effective_user.id):
        await update.message.reply_text(
            "⚠️ You must join @boteratrack and @boterapro to use this bot."
        )
        return ConversationHandler.END

    users.setdefault(user_id, {"bots": [], "referrals": [], "balance": 0})
    save_users(users)
    await update.message.reply_text(
        "Choose a theme for your mini-bot:\n1. Light\n2. Dark\n3. Custom"
    )
    return CHOOSING_THEME

async def theme_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    theme = update.message.text.strip()
    users = load_users()
    bot_info = {"theme": theme, "participants": 0}
    users[user_id]["bots"].append(bot_info)
    save_users(users)
    await update.message.reply_text(
        f"✅ Your mini-bot has been created with theme '{theme}'.\n"
        "Share your referral link to earn rewards!"
    )
    return ConversationHandler.END

async def referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    await update.message.reply_text(
        f"Share this link: https://t.me/{context.bot.username}?start={user_id}"
    )

# -------------------------------
# Telegram Bot Setup
# -------------------------------
def start_bot():
    application = Application.builder().token(TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("create", create)],
        states={CHOOSING_THEME: [MessageHandler(filters.TEXT & ~filters.COMMAND, theme_chosen)]},
        fallbacks=[]
    )
    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("referral", referral))
    print("Main bot running... 🚀")
    application.run_polling()