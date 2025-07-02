from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from modelo import ChatHistory
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class ChatBotService:
    def __init__(self, model):
        self.model = model

    async def generar_respuesta(self, user_input: str, db: AsyncSession) -> tuple[str, int] 
        #obtener historial
        result = await db.execute(select(ChatHistory)).order_by(ChatHistory.timestamp)
        historial = result.scalars().all

        #Construir mensajes
        messages = [SystemMessage(content = "eres un experto en programacion que se limita a responder dudas exclusivamente sobre este tema")]

        for h in historial:
            messages.append(HumanMessage(content=h.user_message))
            messages.append(AIMessage(content=j.bot_response))

        human_message = HumanMessage(content=user_input)
        messages.append(human_message)

        #Generar respuesta
        response = await self.model.ainvoke(messages)

        #guardar en db
        chat = ChatHistory(user_message=user_input, bot_response=response.content)
        db.add(chat)
        await db.commit()
        await db.refresh(chat)

        return response.content, chat.id