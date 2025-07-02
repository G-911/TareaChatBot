import os
import asyncio 
import httpx

from modelo import ChatHistory, SessionLocal
from servicio.chatbot_service import ChatBotService
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from telegram_bot import start_telegram_bot, stop_telegram_bot

#Importamos las variables de entorno
load_dotenv()

#Instanciamos fastApi
app = FastAPI(debug = True)

#Inicializamos el modelo
model = init_chat_model("command-r-plus", model_provider = "cohere")

#Creamos una variable que almacene la contrasena de API_KEY
API_KEY = os.getenv("API_KEY")

#Funcion para confirmar nuestra contrasena
async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code = 403, detail = "Clave de Api no valida")


####    PAGINA    ####
class Bot(BaseModel):
    query : str

#Funcion para asegurarnos de que la sesion siempre se cierre
async def get_db():
    async with SessionLocal() as session:
        yield session

@app.on_event("startup")
async def startup():
    from modelo import init_models
    await init_models()
    await start_telegram_bot()# si comento esta linea no se inicia el bot de telegram

@app.on_event("shutdown")
async def shutdown():
    await stop_telegram_bot()

@app.get("/")
async def root():
    return {"message": "hola"}

@app.post("/response")
async def uest(bot: Bot, 
                      api_key: str = Depends(verify_api_key),
                      db: AsyncSession = Depends(get_db)):
    try:
        #Cargamos los mensajes previos del usuario
        result = await db.execute(select(ChatHistory).order_by(ChatHistory.timestamp))

#revisar
        # para limitar los mensajes recordados a 10
        # result = await db.execute(
        #     select(ChatHistory).order_by(ChatHistory.timestamp.desc()).limit(10)
        # )
        # historial = reversed(result.scalars().all())


        historial = result.scalars().all()

        #Creamos un arreglo que va acontener nuestro chat con el agente
        messages = [SystemMessage(content = "eres un experto en programacion que responde dudas unicamente sobre ese tema")]

        for h in historial:
            messages.append(HumanMessage(content = h.user_message))
            messages.append(AIMessage(content = h.bot_response))
        
        human_message = HumanMessage(content = bot.query)
        messages.append(human_message)

        response = await model.ainvoke(messages)
        messages.append(response)

        chat = ChatHistory(
            user_message = bot.query,
            bot_response =  response.content
        )
        db.add(chat)
        await db.commit()
        await db.refresh(chat)
        return {"response": response.content, "id": chat.id}
    
    except Exception as e:
        return JSONResponse(status_code = 500, content = {"error": str(e)})