from fastapi import APIRouter
from app.api.endpoints import routes, charging_stations

api_router = APIRouter()
api_router.include_router(routes.router, prefix="/v1/routes", tags=["routes"])
api_router.include_router(charging_stations.router, prefix="/v1/charging-stations", tags=["charging-stations"])
