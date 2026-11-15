import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-3.8-flash")

async def send_long_message(message, text):
    # Telegram allows max 4096 characters per message, so split into chunks
    for i in range(0, len(text), 4000):
        await message.reply_text(text[i:i+4000])
        await asyncio.sleep(1)  # small pause between messages

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi! I'm working now. Send me any message or a photo of a math problem."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    try:
        if message.photo:
            await message.reply_text("Solving... please wait")
            photo = message.photo[-1]
            file = await context.bot.get_file(photo.file_id)
            photo_bytes = await file.download_as_bytearray()
            prompt = "Solve this math problem step by step. Show clear working and final answer."
            response = model.generate_content([
                prompt,
                {"mime_type": "image/jpeg", "data": bytes(photo_bytes)}
            ])
        else:
            response = model.generate_content(message.text)

        # Use the chunk-sender for both text and photo answers
        await send_long_message(message, response.text)

    except Exception as e:
        # If anything fails, tell the user instead of going silent
        await message.reply_text("Error: " + str(e))

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO | filters.TEXT, handle_message))
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
