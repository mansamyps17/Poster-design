import os
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from PIL import Image
import asyncio

TOKEN = os.getenv("BOT_TOKEN")
app = Flask(__name__)

telegram_app = Application.builder().token(TOKEN).build()

async def start(update: Update, context):
    await update.message.reply_text("សួស្ដី! សូមផ្ញើរូបភាពផលិតផលរបស់អ្នកមក ដើម្បីខ្ញុំបង្កើត Poster ហាងជូន។")

async def handle_photo(update: Update, context):
    await update.message.reply_text("កំពុងច្នៃ Poster ជូន សូមរង់ចាំបន្តិច...")
    
    try:
        # ១. យក File រូបភាពដែល User ផ្ញើមក
        photo_file = await update.message.photo[-1].get_file()
        photo_path = "downloaded_product.jpg"
        await photo_file.download_to_drive(photo_path)
        
        # ២. បើក Template Poster របស់ហាង (ត្រូវមានไฟล์ template.jpg ក្នុង GitHub)
        if os.path.exists("template.jpg"):
            poster = Image.open("template.jpg").convert("RGBA")
        else:
            # បើអត់ទាន់មាន template.jpg វានឹងបង្កើតផ្ទាំងស ១០៨០x១០៨០ ជំនួសសិន
            poster = Image.new("RGBA", (1080, 1080), (255, 255, 255, 255))
            
        # ៣. កែទំហំរូបភាពផលិតផល និងយកមកបិទភ្ជាប់លើ Poster (កំណត់ទីតាំងตามចិត្ត X, Y)
        product_img = Image.open(photo_path).convert("RGBA")
        product_img = product_img.resize((600, 600)) # កែទំហំរូបផលិតផល
        
        # ទីតាំង坐标 (X=240, Y=150) សម្រាប់ដាក់រូបផលិតផលលើ Template
        poster.paste(product_img, (240, 150), product_img if product_img.mode == 'RGBA' else None)
        
        output_path = "final_poster.png"
        poster.convert("RGB").save(output_path)
        
        # ៤. ส่งរូប Poster ត្រឡប់ទៅ Telegram វិញ
        await update.message.reply_photo(photo=open(output_path, 'rb'), caption="✨ នេះជា Poster ផលិតផលរបស់អ្នក!")
        
    except Exception as e:
        await update.message.reply_text(f"មានបញ្ហាក្នុងការបង្កើត Poster: {str(e)}")

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
