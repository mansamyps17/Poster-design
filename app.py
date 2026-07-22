import os
import requests
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from PIL import Image, ImageDraw, ImageFont
import asyncio

TOKEN = os.getenv("BOT_TOKEN")
PHOTOROOM_API_KEY = os.getenv("PHOTOROOM_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") # ត្រូវបញ្ចូល OpenAI Key លើ Render ផងដែរ

app = Flask(__name__)
telegram_app = Application.builder().token(TOKEN).build()

async def start(update: Update, context):
    await update.message.reply_text("សួស្ដី! សូមផ្ញើរូបភាពផលិតផលរបស់អ្នកមក ខ្ញុំនឹងប្រើប្រាស់ AI Design បង្កើត Poster ស្អាតដូច Khmum AI ជូន។")

async def handle_photo(update: Update, context):
    await update.message.reply_text("🎨 កំពុងបង្កើតរូបភាពដោយ AI... សូមរង់ចាំបន្តិច (អាចចំណាយពេលបន្តិច)។")
    
    try:
        # ១. ດາວໂຫຼດរូបភាពពី Telegram
        photo_file = await update.message.photo[-1].get_file()
        input_path = "input_product.png"
        await photo_file.download_to_drive(input_path)
        
        # ២. កាត់ Background ចេញដោយ Photoroom API
        photoroom_url = "https://sdk.photoroom.com/v1/segment"
        headers = {"x-api-key": PHOTOROOM_API_KEY}
        
        with open(input_path, "rb") as image_file:
            files = {"image_file": image_file}
            response = requests.post(photoroom_url, headers=headers, files=files)
            
        if response.status_code != 200:
            await update.message.reply_text("មានបញ្ហាក្នុងការកាត់ Background។")
            return
            
        transparent_path = "transparent_product.png"
        with open(transparent_path, "wb") as out_file:
            out_file.write(response.content)
            
        # ៣. ប្រើ OpenAI DALL-E ដើម្បី Generate Background ស្អាតបែប Studio
        openai_url = "https://api.openai.com/v1/images/generations"
        openai_headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        openai_data = {
            "model": "dall-e-3",
            "prompt": "A luxury modern minimalist product photography studio background, soft warm lighting, elegant shelf, high-end commercial style, 1080x1080",
            "n": 1,
            "size": "1024x1024"
        }
        
        ai_res = requests.post(openai_url, headers=openai_headers, json=openai_data)
        if ai_res.status_code == 200:
            bg_url = ai_res.json()["data"][0]["url"]
            bg_data = requests.get(bg_url).content
            bg_path = "ai_background.jpg"
            with open(bg_path, "wb") as bg_file:
                bg_file.write(bg_data)
                
            # ៤. ផ្គុំ Background និងរូបផលិតផលចូលគ្នាដោយ Pillow
            bg_img = Image.open(bg_path).convert("RGBA").resize((1080, 1080))
            product_img = Image.open(transparent_path).convert("RGBA")
            
            # កែទំហំរូបផលិតផល និងដាក់ចំកណ្ដាល
            product_img = product_img.resize((550, 550))
            bg_img.paste(product_img, (265, 280), product_img)
            
            # ៥. បន្ថែមអត្ថបទចំណងជើងខ្មែរពីលើ Poster
            draw = ImageDraw.Draw(bg_img)
            try:
                # ត្រូវមានไฟล์ Font ភាសាខ្មែរ (ឧ. Koulen.ttf ឬ Battambang.ttf) ក្នុង GitHub
                font = ImageFont.truetype("KhmerOS_battambang.ttf", 60)
            except:
                font = ImageFont.load_default()
                
            # សរសេរអត្ថបទចំណងជើង (Heading)
            draw.text((250, 100), "✨ ផលិតផលគុណភាពខ្មែរ ល្អដាច់គេ ✨", fill="gold", font=font)
            
            output_path = "final_khmum_poster.png"
            bg_img.convert("RGB").save(output_path)
            
            # ៦. ផ្ញើលទ្ធផលទៅ Telegram
            await update.message.reply_photo(
                photo=open(output_path, 'rb'), 
                caption="✨ បង្កើត Poster ជាមួយ AI បានជោគជ័យស្អាតដូច Khmum AI!"
            )
        else:
            await update.message.reply_text("មិនអាចสร้าง AI Background បានទេ សូមពិនិត្យ OpenAI API Key។")
            
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
    return "AI Design Bot is running!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
