import os
import io
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")  # good free model for vision + math

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    # If user sent a photo
    if message.photo:
        await message.reply_text("Solving... please wait")
        photo = message.photo[-1]  # highest quality
        file = await context.bot.get_file(photo.file_id)
        photo_bytes = await file.download_as_bytearray()

        # Send photo + prompt to Gemini
        prompt = "Solve this math problem step by step. Show clear working and final answer."
        response = model.generate_content([
            prompt,
            {"mime_type": "image/jpeg", "data": photo_bytes}
        ])
        await message.reply_text(response.text)

    # If user sent only text
    elif message.text:
        response = model.generate_content(message.text)
        await message.reply_text(response.text)

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.PHOTO | filters.TEXT, handle_message))
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()