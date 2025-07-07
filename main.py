import logging

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router as api_router
from bot_telegram.telegram_bot import start_telegram_bot, stop_telegram_bot

app = FastAPI(debug=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173/"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.on_event("startup")
async def startup():
    logging.getLogger(__name__).info("Iniciando bot de Telegram")
    await start_telegram_bot()

@app.on_event("shutdown")
async def shutdown():
    await stop_telegram_bot()

@app.get("/")
async def root():
    return {"message": "hola"}

app.include_router(api_router)

app.mount("/", StaticFiles(directory="bot_front", html=True), name="static")
