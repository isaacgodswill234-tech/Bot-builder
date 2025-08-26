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
    context.user_data['must_join'] = ["https://t.me/boteratrack", "https://t.me/boterapro"]
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
            # Simulate new participant joining
            if bot_info["participants"] < max_participants:
                bot_info["participants"] += 1

                # Example: referral rewards
                if bot_info["referral_enabled"]:
                    # Give owner ₦1 per participant
                    users[owner_id]["balance"] += 1
                    # Optionally, handle referral chain for 0.5 ₦ per referral (simulation)
                    # You can expand this with real referral tracking later

            save_users(users)
        except Exception as e:
            print(f"Error in mini-bot thread: {e}")
        time.sleep(10)  # check every 10 seconds

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

    print("Bot Factory running... 🚀")
    application.run_polling()

if __name__ == "__main__":
    main()