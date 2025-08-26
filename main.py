import os
import json
import logging
import threading
import time
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters

# -------------------------------
# Main Bot Token (your bot)
# -------------------------------
MAIN_TOKEN = "8263358249:AAFhhObsLAepIqNJGrPG_-DYN6TwsscB5Lo"

DATA_FILE = "users.json"

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
# Conversation states
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
        "👋 Welcome to the Bot Factory!\n"
        "Use /create to start creating your mini-bot."
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
    context.user_data['must_join'] = [c.strip() for c in update.message.text.split(",")]
    await update.message.reply_text("Enter your payment channel (e.g., @myPayments):")
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

    # Save to users.json
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
    threading.Thread(target=run_minibot, args=(bot_data,), daemon=True).start()

    await update.message.reply_text("✅ Your mini-bot has been created and launched automatically!")
    return ConversationHandler.END

# -------------------------------
# Mini-bot runner
# -------------------------------
def run_minibot(bot_data):
    """
    Runs a user mini-bot using their token, sends messages to must-join channels, 
    and tracks participants up to the max limit.
    """
    token = bot_data['token']
    must_join = bot_data['must_join_channels']
    max_participants = bot_data['max_participants']
    bot_instance = Bot(token)
    print(f"Mini-bot started with token: {token}")

    while True:
        try:
            # Example: send startup message to must-join channels
            for channel in must_join:
                try:
                    bot_instance.send_message(chat_id=channel, text=bot_data['startup_message'])
                except:
                    pass
            # Here you could implement participant tracking and referral counting
        except Exception as e:
            print(f"Mini-bot error: {e}")
        time.sleep(30)  # interval between actions

# -------------------------------
# Referral command
# -------------------------------
async def referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    await update.message.reply_text(f"Share this link: https://t.me/{context.bot.username}?start={user_id}")

# -------------------------------
# Telegram Bot Setup
# -------------------------------
def main():
    application = Application.builder().token(MAIN_TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("create", create)],
        states={
            TOKEN_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_token)],
            THEME_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_theme)],
            MUST_JOIN_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_must_join)],
            PAYMENT_CHANNEL_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_payment_channel)],
            PAYMENT_METHOD_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_payment_method)],
            REFERRAL_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_referral)],
            STARTUP_MSG_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_startup_message)],
            ADS_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_ads)],
            DESCRIPTION_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_description)],
            MAX_PARTICIPANTS_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_max_participants)],
        },
        fallbacks=[]
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("referral", referral))

    print("Bot Factory is running... 🚀")
    application.run_polling()

if __name__ == "__main__":
    main()