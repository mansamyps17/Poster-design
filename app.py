import os
import requests
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import asyncio

TOKEN = os.getenv("BOT_TOKEN")
PHOTOROOM_API_KEY = os.getenv("PHOTOROOM_API_KEY")

app = Flask(__name__)
telegram_app = Application.builder().token(TOKEN).build()

async def start(update: Update, context):
    await update.message.reply_text("សួស្ដី! សូមផ្ញើរូបភាពផលិតផលរបស់អ្នកមក ខ្ញុំនឹងប្រើប្រាស់ AI កាត់ត Poster ស្អាតដូចក្នុងស្ទូឌីយោជូន។")

async def handle_photo(update: Update, context):
    await update.message.reply_text("🎨 កំពុងបង្កើតរូបភាពដោយ AI... សូមរង់ចាំបន្តិច។")
    
    try:
        # ១. យក File រូបភាពដែល User ផ្ញើមក
        photo_file = await update.message.photo[-1].get_file()
        input_path = "input_product.jpg"
        await photo_file.download_to_drive(input_path)
        
        # ២. ส่งไปยัง Photoroom API เพื่อลบ Background และสร้าง AI Studio Studio Background
        url = "https://image-api.photoroom.com/v2/edit"
        headers = {"x-api-key": PHOTOROOM_API_KEY}
        
        with open(input_path, "rb") as image_file:
            files = {"imageFile": image_file}
            data = {
                "background.color": "FFFFFF",
                "shadow.mode": "ai.soft",
                "padding": "0.1"
            }
            
            response = requests.post(url, headers=headers, files=files, data=data)
            
        if response.status_code == 200:
            output_path = "ai_poster.jpg"
            with open(output_path, "wb") as output_file:
                output_file.write(response.content)
                
            # ៣. ផ្ញើរូបភាព AI ត្រឡប់ទៅ Telegram វិញ
            await update.message.reply_photo(
                photo=open(output_path, 'rb'), 
                caption="✨ បង្កើតរូបភាពដោយ AI បានជោគជ័យ!"
            )
        else:
            await update.message.reply_text(f"ขออภัย ระบบ AI មិនអាចประมวลผลได้: {response.text}")
            
    except Exception as e:
        await update.message.reply_text(f"មានបញ្ហាក្នុងការដំណើរការ: {str(e)}")

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
