# FormatAI/app/api/v1/api.py

from fastapi import APIRouter
from app.api.v1.endpoints import format

api_router = APIRouter()
api_router.include_router(format.router, prefix="/transform", tags=["Transformação"])
# Futuramente, podemos adicionar outros routers aqui
# api_router.include_router(users.router, prefix="/users", tags=["Users"])