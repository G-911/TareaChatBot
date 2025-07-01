from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from datetime import datetime

#URL de conexion a la base de datos
DATABASE_URL = "sqlite+aiosqlite:///./test.db"
#crear motor asuncrono
engine = create_async_engine(DATABASE_URL, echo = True)
#declaracion de la base de datos
Base = declarative_base()
#Crear la sesion asincrona
SessionLocal = sessionmaker( bind = engine,
                             class_ = AsyncSession,
                             expire_on_commit = False,
                             autocommit = False,
                             autoflush = False
                             )
#esto asegura que se cree correctamente una sesion asincrona y que los 
#objetos no se buelvan inestables despues de hacer un commit


#Modelo de historial de chat
class ChatHistory(Base):
    __tablename__ = "chat_history"
    id = Column(Integer, primary_key = True, index = True)
    user_message = Column(String)
    bot_response = Column(String)
    timestamp = Column(DateTime, default = datetime.utcnow)

#Inicializacion de la base de datos
async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


__all__ = ["ChatHistory", "SessionLocal", "init_models"]


#Crear una base de datos sincrona
# engine = create_engine(DATABASE_URL, 
#                        connect_args = {"check_same_thread": False})
