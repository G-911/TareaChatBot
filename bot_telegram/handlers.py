from telegram import Update
from telegram.ext import ContextTypes
from .client import obtener_respuesta

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    respuesta = await obtener_respuesta(user_input)
    await update.message.reply_text(respuesta)
    print(f"Mensaje recibido de Telegram: {user_input}")