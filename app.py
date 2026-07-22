import os
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from PIL import Image, ImageDraw
import asyncio

TOKEN = os.getenv("BOT_TOKEN")
app = Flask(__name__)

bot = Bot(token=TOKEN)
telegram_app = Application.builder().token(TOKEN).updater(None).build()

# ពេលអតិថិជនវាយ /start
async def start(update: Update, context):
    await update.message.reply_text("សួស្ដី! សូមផ្ញើរូបភាពផលិតផលរបស់អ្នកមក ដើម្បីខ្ញុំបង្កើត Poster ជូន។")

# ពេលអតិថិជនផ្ញើរូបភាពមក
async def handle_photo(update: Update, context):
    await update.message.reply_text("ได้รับរូបភាពហើយ! កំពុងបង្កើត Poster ជូន... (រង់ចាំអភិវឌ្ឍន៍បន្ថែម)")

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    
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
