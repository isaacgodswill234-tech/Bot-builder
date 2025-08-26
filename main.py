import os
import json
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# -------------------------------
# Your Bot Token (hardcoded)
# -------------------------------
TOKEN = "8263358249:AAFhhObsLAepIqNJGrPG_-DYN6TwsscB5Lo"

DATA_FILE = "users.json"

def load_users():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(DATA_FILE, "w") as f:
        json.dump(users, f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to Bot Builder!\n\n"
        "Use /create <bot_token> to build your own bot.\n"
        "📢 Free bots show ads. Upgrade to Premium to remove ads."
    )

async def create(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = load_users()
    user_id = str(update.effective_user.id)

    if len(context.args) != 1:
        await update.message.reply_text("⚠️ Usage: /create <bot_token>")
        return

    bot_token = context.args[0]
    users[user_id] = {"token": bot_token, "premium": False}
    save_users(users)

    await update.message.reply_text(
        "✅ Your bot has been saved!\n"
        "It will include ads unless you switch to Premium."
    )

async def toggle_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = load_users()
    user_id = str(update.effective_user.id)

    if user_id not in users:
        await update.message.reply_text("❌ You don’t have a bot yet. Use /create first.")
        return

    users[user_id]["premium"] = not users[user_id]["premium"]
    save_users(users)
    status = "Premium (No ads)" if users[user_id]["premium"] else "Free (Ads enabled)"
    await update.message.reply_text(f"🔄 Your plan has been updated: {status}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("create", create))
    app.add_handler(CommandHandler("premium", toggle_premium))
    print("Bot is running... 🚀")
    app.run_polling()

if __name__ == "__main__":
    main()