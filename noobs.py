import os
import asyncio 
import httpx
import logging

from modelo import ChatHistory, SessionLocal
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot_telegram.noob_telegram_bot import start_telegram_bot, stop_telegram_bot

# Importamos las variables de entorno
load_dotenv()

# Instanciamos fastApi
app = FastAPI(debug = True)

####    UNIMOS CON VUE      ####
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Inicializamos el modelo
model = init_chat_model("command-r-plus", model_provider = "cohere")

#Creamos una variable que almacene la contrasena de API_KEY
API_KEY = os.getenv("API_KEY")

# Funcion para confirmar nuestra contrasena
async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code = 403, detail = "Clave de Api no valida")


####    PAGINA    ####
class Bot(BaseModel):
    query : str

# Funcion para asegurarnos de que la sesion siempre se cierre
async def get_db():
    async with SessionLocal() as session:
        yield session

@app.on_event("startup")
async def startup():
    logger = logging.getLogger(__name__)
    logger.info("llamando a start_telegram_bot")
    await start_telegram_bot()# si comento esta linea no se inicia el bot de telegram

@app.on_event("shutdown")
async def shutdown():
    # print("cerrando conexion telegram")
    await stop_telegram_bot()

@app.get("/")
async def root():
    return {"message": "hola"}

@app.post("/response")
async def bot_requsest(bot: Bot, 
                      x_api_key: str = Depends(verify_api_key),
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
        messages = [SystemMessage(content = """
            Eres un asistente de inteligencia artificial especializado exclusivamente en programación. Tu única función es responder preguntas técnicas relacionadas con el desarrollo de software. No debes responder, comentar ni especular sobre ningún tema que no esté directamente relacionado con programación práctica.

            ✅ Puedes ayudar con:
            - Lenguajes de programación (Python, JavaScript, Java, C++, etc.)
            - Algoritmos y estructuras de datos
            - Bases de datos y consultas SQL
            - Frameworks, librerías y herramientas de desarrollo
            - Depuración de errores y buenas prácticas de codificación
            - Testing automatizado y pruebas de software
            - Control de versiones (como Git)
            - Integración de APIs y desarrollo web
            - DevOps, CI/CD o infraestructura solo si están relacionados con scripts, configuración de código o automatización técnica
            - Inteligencia artificial y machine learning solo si se trata de implementación en código (por ejemplo, uso de librerías como TensorFlow, PyTorch, scikit-learn, LangChain, etc.)

            🚫 No debes responder preguntas sobre:
            - Temas personales, filosóficos o de opinión
            - Noticias, historia, política o cultura general
            - Conceptos teóricos de IA sin relación con código
            - Recomendaciones de carrera, consejos de estudio o motivación
            - Cualquier tema no relacionado con programación práctica

            Si el usuario hace una pregunta fuera de tu dominio, responde de forma educada pero firme con algo como:
            "Lo siento, solo puedo ayudarte con temas estrictamente relacionados con programación y desarrollo de software."

            Mantén un tono técnico, claro y directo. Siempre que sea posible, incluye ejemplos de código bien explicados. Si la pregunta es ambigua, solicita más detalles antes de responder.
            """
        )]

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
    
# Para garantizar que fastApi registre el resto de las rutas primero
app.mount("/", StaticFiles(directory="bot_front", html=True), name="static")
