import os
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import asyncio

TOKEN = os.getenv("BOT_TOKEN")
app = Flask(__name__)

# កសាង Application ឲ្យបានត្រឹមត្រូវតាមស្តង់ដារថ្មី
telegram_app = Application.builder().token(TOKEN).build()

async def start(update: Update, context):
    await update.message.reply_text("សួស្ដី! សូមផ្ញើរូបភាពផលិតផលរបស់អ្នកមក ដើម្បីខ្ញុំបង្កើត Poster ជូន។")

async def handle_photo(update: Update, context):
    await update.message.reply_text("ទទួលបានរូបភាពហើយ! កំពុងបង្កើត Poster ជូន...")

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_data = request.get_json(force=True)
    
    async def process():
        async with telegram_app:
            update = Update.de_json(json_data, telegram_app.bot)
            await telegram_app.initialize()
            await telegram_app.process_update(update)
            
    asyncio.run(process())
    return "OK", 200

@app.route("/", methods=["GET"])
def index():
    return "Bot is running!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
