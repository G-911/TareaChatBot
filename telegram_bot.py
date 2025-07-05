import os, httpx, asyncio

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv


load_dotenv()
telegram_app = None

#Creamos una variable que almacene nuestra API_KEY
API_KEY = os.getenv("API_KEY")
#Creamos una variable que almacene nuestro token de telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

#Conectamos FastApi con telegram
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "http://localhost:8000/response",
                headers = {"x-api-key": API_KEY},
                json = {"query": user_input}
            )
            data = response.json()
            await update.message.reply_text(data.get("response", "Error en la respuesta"))
            print(f"mensaje recibido de telegram: {user_input}")
    except httpx.ReadTimeout:
        await update.message.reply_text("⏱️ El servidor tardó demasiado en responder.")
    except httpx.HTTPStatusError as e:
        await update.message.reply_text(f"❌ Error del servidor: {e.response.status_code}")
    except httpx.RequestError as e:
        await update.message.reply_text("❌ No se pudo contactar con el servidor.")
        print(f"Error de red: {e}")
    except Exception as e:
        await update.message.reply_text("❌ Ocurrió un error inesperado.")
        print(f"Error inesperado: {e}")



#Funcion para iniciar el bot de telegram
async def start_telegram_bot():
    try:
        global telegram_app
        print("iniciando e bot de Telegram")
        telegram_app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        print("bot construido")
        telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        await telegram_app.initialize()
        print("bot inicializado")
        await telegram_app.start() #Corre en segundo plano
        print("bot de telegram en ejecucion")
        await telegram_app.updater.start_polling() # <-- importante para recibir mensajes

        await telegram_app.updater.wait() # < -- mantiene el bot vivo
    
    except Exception as e:
        print(f"Error al inicializar el bot de telegram")


#Funcion para detener el bot de telegram
async def stop_telegram_bot():
    if telegram_app:
        await telegram_app.stop()


#para correr dentro de main.py
# if __name__ == "__main__":
#     app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
#     app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
#     asyncio.run(app.run_polling())
