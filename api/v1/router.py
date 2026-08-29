from fastapi import APIRouter
from api.v1.endpoints import auth, logs, medications, streaks


api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(medications.router)
api_router.include_router(logs.router)
api_router.include_router(streaks.router)