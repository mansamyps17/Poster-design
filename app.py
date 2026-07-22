import os
import requests
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from PIL import Image, ImageDraw, ImageFont
import asyncio

TOKEN = os.getenv("BOT_TOKEN")
PHOTOROOM_API_KEY = os.getenv("PHOTOROOM_API_KEY")

app = Flask(__name__)
telegram_app = Application.builder().token(TOKEN).build()

async def start(update: Update, context):
    await update.message.reply_text("សួស្ដី! សូមផ្ញើរូបភាពផលិតផលរបស់អ្នកមក ខ្ញុំនឹងប្រើប្រាស់ AI ជំនួយបង្កើត Poster ស្អាតជូន។")

async def handle_photo(update: Update, context):
    await update.message.reply_text("🎨 កំពុងបង្កើត Poster ដោយ AI... សូមរង់ចាំបន្តិច។")
    
    try:
        # ១. ទាញយករូបភាពពី Telegram
        photo_file = await update.message.photo[-1].get_file()
        input_path = "input_product.png"
        await photo_file.download_to_drive(input_path)
        
        # ២. ប្រើ Photoroom API ដើម្បីកាត់ Background និងដាក់ Studio Background ស្វ័យប្រវត្តិ
        url = "https://image-api.photoroom.com/v2/edit"
        headers = {"x-api-key": PHOTOROOM_API_KEY}
        
        with open(input_path, "rb") as image_file:
            files = {"imageFile": image_file}
            data = {
                "background.preset": "studio-modern-white",
                "shadow.mode": "ai.soft",
                "padding": "0.1"
            }
            
            response = requests.post(url, headers=headers, files=files, data=data)
            
        if response.status_code == 200:
            bg_removed_path = "photoroom_output.jpg"
            with open(bg_removed_path, "wb") as out_file:
                out_file.write(response.content)
                
            # ៣. បើករូបដែលកាត់តរួច មកបន្ថែមអត្ថបទចំណងជើងខ្មែរពីលើ
            poster = Image.open(bg_removed_path).convert("RGBA")
            poster = poster.resize((1080, 1080))
            
            draw = ImageDraw.Draw(poster)
            try:
                font = ImageFont.truetype("KhmerOSbattambang.ttf", 50)
            except:
                font = ImageFont.load_default()
                
            # សរសេរអត្ថបទខ្មែរ (អាចកែតម្រូវទីតាំង X, Y តាមចិត្ត)
            draw.text((250, 60), "✨ ផលិតផលគុណភាពខ្ពស់ ល្អដាច់គេ ✨", fill="black", font=font)
            
            output_path = "final_poster.png"
            poster.convert("RGB").save(output_path)
            
            # ៤. ផ្ញើលទ្ធផលទៅ Telegram
            await update.message.reply_photo(
                photo=open(output_path, 'rb'), 
                caption="✨ បង្កើត Poster បានជោគជ័យ!"
            )
        else:
            await update.message.reply_text(f"មានបញ្ហាជាមួយ Photoroom API: {response.text}")
            
    except Exception as e:
        await update.message.reply_text(f"មានបញ្ហាប្រព័ន្ធ: {str(e)}")

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
