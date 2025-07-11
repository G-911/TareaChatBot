from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_core.messages import HumanMessage
from langchain.chat_models import init_chat_model
from httpx import HTTPStatusError

from services.chat_service import construir_historial
from modelo import ChatHistory
from api.dependencies import verify_api_key, get_db

router = APIRouter()
model = init_chat_model("command-r-plus", model_provider="cohere")

class Bot(BaseModel):
    query: str

@router.post("/response")
async def bot_response(
    bot: Bot,
    x_api_key: str = Depends(verify_api_key),
    db: AsyncSession = Depends(get_db)
):
    try:
        # Verifica que la query no esté vacía
        if not bot.query or not isinstance(bot.query, str):
            return JSONResponse(
                status_code=422,
                content={"error": "El campo 'query' es obligatorio y debe ser un texto."}
            )

        # Construir historial y preparar mensaje
        messages = await construir_historial(db)
        messages.append(HumanMessage(content=bot.query))
        # Invocar el modelo
        response = await model.ainvoke(messages)
        
        model_output = response.content.strip() if response and isinstance(response.content, str) else None

        # Fallback si el modelo no responde
        bot_output = model_output if model_output else "🤖 No pude generar una respuesta en este momento."

        # Guardar historial en la base de datos
        chat = ChatHistory(user_message=bot.query, bot_response=bot_output)
        db.add(chat)
        await db.commit()
        await db.refresh(chat)
        print("📦 Respuesta cruda:", response.text)
        print(f"el query: {bot.query}")
        print("🔍 Respuesta del servidor:", response.text)

        # Retornar JSON válido
        return JSONResponse(
            status_code=200,
            content={"response": bot_output, "id": chat.id}
        )

    except HTTPStatusError as e:
        return JSONResponse(
            status_code=e.response.status_code,
            content={"error": f"{e.response.status_code} - {e.response.text}"}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error interno: {str(e)}"}
        )
    
    