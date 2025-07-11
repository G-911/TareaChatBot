from fastapi import Header, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from modelo import SessionLocal
from config.settings import API_KEY

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, details="Clave de API no valida")
    
async def get_db():
    async with SessionLocal() as session:
        yield session