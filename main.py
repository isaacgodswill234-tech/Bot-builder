import os
import json
import logging
import threading
import time
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters

# -------------------------------
# Main Bot Token
# -------------------------------
MAIN_TOKEN = "YOUR_MAIN_BOT_TOKEN"
DATA_FILE = "users.json"
MAIN_ADMIN_ID = 123456789  # 🔴 Replace with your Telegram user ID

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
# Conversation States
# -------------------------------
(
    TOKEN_STATE,
    THEME_STATE,
    MUST_JOIN_STATE,
    PAYMENT_CHANNEL_STATE,
    PAYMENT_METHOD_STATE,
    REFERRAL_STATE,
    STARTUP_MSG_STATE,
    ADS_STATE,
    DESCRIPTION_STATE,
    MAX_PARTICIPANTS_STATE
) = range(10)

# -------------------------------
# Start command
# -------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to the Bot Factory!\nUse /create to start creating your mini-bot."
    )

# -------------------------------
# Create bot flow
# -------------------------------
async def create(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Enter your BotFather token for your mini-bot:")
    return TOKEN_STATE

async def get_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['bot_token'] = update.message.text.strip()
    await update.message.reply_text("Choose a theme: Light, Dark, Custom")
    return THEME_STATE

async def get_theme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['theme'] = update.message.text.strip()
    await update.message.reply_text("Enter must-join channels (comma-separated, e.g., @channel1,@channel2):")
    return MUST_JOIN_STATE

async def get_must_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Force these two channels as must-join
    context.user_data['must_join'] = [
        "https://t.me/boteratrack",
        "https://t.me/boterapro"
    ]
    await update.message.reply_text(
        "✅ Your mini-bot participants must join the required channels automatically."
        "\nEnter your payment channel (e.g., @myPayments):"
    )
    return PAYMENT_CHANNEL_STATE

async def get_payment_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['payment_channel'] = update.message.text.strip()
    await update.message.reply_text("Enter payment method (Bank Transfer, USDT, PayPal, etc.):")
    return PAYMENT_METHOD_STATE

async def get_payment_method(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['payment_method'] = update.message.text.strip()
    await update.message.reply_text("Enable referral system? (yes/no):")
    return REFERRAL_STATE

async def get_referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['referral_enabled'] = update.message.text.strip().lower() == "yes"
    await update.message.reply_text("Enter startup message for your mini-bot:")
    return STARTUP_MSG_STATE

async def get_startup_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['startup_message'] = update.message.text.strip()
    await update.message.reply_text("Enable ads/premium? (yes/no):")
    return ADS_STATE

async def get_ads(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['ads_enabled'] = update.message.text.strip().lower() == "yes"
    await update.message.reply_text("Enter a short description of your bot:")
    return DESCRIPTION_STATE

async def get_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['description'] = update.message.text.strip()
    await update.message.reply_text("Enter max participants for your mini-bot (number):")
    return MAX_PARTICIPANTS_STATE

async def get_max_participants(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        max_participants = int(update.message.text.strip())
    except:
        max_participants = 500
    context.user_data['max_participants'] = max_participants

    # Save mini-bot data
    user_id = str(update.effective_user.id)
    users = load_users()
    users.setdefault(user_id, {"bots": [], "referrals": [], "balance": 0})
    bot_data = {
        "token": context.user_data['bot_token'],
        "theme": context.user_data['theme'],
        "must_join_channels": context.user_data['must_join'],
        "payment_channel": context.user_data['payment_channel'],
        "payment_method": context.user_data['payment_method'],
        "referral_enabled": context.user_data['referral_enabled'],
        "startup_message": context.user_data['startup_message'],
        "ads_enabled": context.user_data['ads_enabled'],
        "description": context.user_data['description'],
        "participants": 0,
        "max_participants": context.user_data['max_participants']
    }
    users[user_id]["bots"].append(bot_data)
    save_users(users)

    # Launch mini-bot thread
    threading.Thread(target=run_minibot, args=(user_id, bot_data), daemon=True).start()

    await update.message.reply_text("✅ Your mini-bot has been created and launched automatically!")
    return ConversationHandler.END

# -------------------------------
# Mini-bot runner with participant & referral tracking
# -------------------------------
def run_minibot(owner_id, bot_data):
    token = bot_data['token']
    must_join = bot_data['must_join_channels']
    max_participants = bot_data['max_participants']
    bot_instance = Bot(token)
    print(f"Mini-bot started for user {owner_id} with token {token}")

    users = load_users()
    bot_info = users[owner_id]["bots"][-1]

    while True:
        try:
            if bot_info["participants"] < max_participants:
                bot_info["participants"] += 1
                if bot_info["referral_enabled"]:
                    users[owner_id]["balance"] += 1
            save_users(users)
        except Exception as e:
            print(f"Error in mini-bot thread: {e}")
        time.sleep(10)

# -------------------------------
# Referral command
# -------------------------------
async def referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    await update.message.reply_text(f"Share this link: https://t.me/{context.bot.username}?start={user_id}")

# -------------------------------
# Balance check command
# -------------------------------
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    users = load_users()
    bal = users.get(user_id, {}).get("balance", 0)
    await update.message.reply_text(f"💰 Your current balance: ₦{bal}")

# -------------------------------
# Broadcasts
# -------------------------------
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Main admin broadcast to ALL users across all mini-bots"""
    if update.effective_user.id != MAIN_ADMIN_ID:
        return await update.message.reply_text("❌ You are not allowed to use this command.")

    if not context.args:
        return await update.message.reply_text("⚠️ Usage: /broadcast <message>")

    msg = " ".join(context.args)
    users = load_users()

    sent_count = 0
    for uid in users.keys():
        try:
            await context.bot.send_message(chat_id=uid, text=f"📢 {msg}")
            sent_count += 1
        except:
            pass

    await update.message.reply_text(f"✅ Broadcast sent to {sent_count} users.")

async def minibot_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mini-bot admin broadcast only to their own bot participants"""
    user_id = str(update.effective_user.id)
    users = load_users()
    if user_id not in users:
        return await update.message.reply_text("❌ You don’t have a mini-bot yet.")

    if not context.args:
        return await update.message.reply_text("⚠️ Usage: /mbroadcast <message>")

    msg = " ".join(context.args)
    bots = users[user_id]["bots"]

    sent_count = 0
    for bot in bots:
        # simulate sending only to owner’s bot participants
        for _ in range(bot["participants"]):
            sent_count += 1

    await update.message.reply_text(f"✅ Mini-bot broadcast sent to {sent_count} of your users.")

# -------------------------------
# Telegram Bot Setup
# -------------------------------
def main():
    application = Application.builder().token(MAIN_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("create", create)],
        states={
            0: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_token)],
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_theme)],
            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_must_join)],
            3: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_payment_channel)],
            4: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_payment_method)],
            5: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_referral)],
            6: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_startup_message)],
            7: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_ads)],
            8: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_description)],
            9: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_max_participants)],
        },
        fallbacks=[]
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("referral", referral))
    application.add_handler(CommandHandler("balance", balance))
    application.add_handler(CommandHandler("broadcast", broadcast))  # Global
    application.add_handler(CommandHandler("mbroadcast", minibot_broadcast))  # Mini-bot

    print("Bot Factory running... 🚀")
    application.run_polling()

if __name__ == "__main__":
    main()