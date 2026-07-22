import os
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from PIL import Image, ImageDraw, ImageFont
import asyncio

TOKEN = os.getenv("BOT_TOKEN")
app = Flask(__name__)

# បង្កើត Bot instance
bot = Bot(token=TOKEN)

# បង្កើត Application សម្រាប់จัดการ Handler ផ្សេងៗ
telegram_app = Application.builder().token(TOKEN).updater(None).build()

async def start(update: Update, context):
    await update.message.reply_text("សួស្ដី! សូមផ្ញើរូបភាពផលិតផល និងព័ត៌មានមក ដើម្បីបង្កើត Poster ហាងរបស់អ្នក។")

# ភ្ជាប់ Command /start
telegram_app.add_handler(CommandHandler("start", start))

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    # ទទួល Request ពី Telegram ហើយបញ្ជូនបន្តទៅ Telegram Application
    update = Update.de_json(request.get_json(force=True), bot)
    
    # ដំណើរការ Async function ក្នុង Flask
    async def process():
        await telegram_app.initialize()
        await telegram_app.process_update(update)
    
    asyncio.run(process())
    return "OK", 200

@app.route("/", methods=["GET"])
def index():
    return "Bot is running!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
