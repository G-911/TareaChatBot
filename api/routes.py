from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_core.messages import HumanMessage
from langchain.chat_models import init_chat_model
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
        messages = await construir_historial(db)
        human_message = HumanMessage(content=bot.query)
        messages.append(human_message)

        response = await model.ainvoke(messages)

        chat = ChatHistory(user_message=bot.query, bot_response=response.content)
        db.add(chat)
        await db.commit()
        await db.refresh(chat)

        return {"response": response.content, "id": chat.id}
    
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


