import asyncio

from telegram.ext import ApplicationBuilder, MessageHandler, filters
from .config import TELEGRAM_TOKEN
from .handlers import handle_message

telegram_app = None

async def start_telegram_bot():
    global telegram_app
    try:
        telegram_app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        await telegram_app.initialize()
        await telegram_app.start()
        asyncio.create_task(telegram_app.updater.start_polling())
    except Exception as e:
        print(f"Error al iniciar el bot de Telegram: {e}")

async def stop_telegram_bot():
    if telegram_app:
        await telegram_app.stop()