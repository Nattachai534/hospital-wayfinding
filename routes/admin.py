from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.get("/stats")
async def get_stats():
    """สถิติระบบ"""
    return {
        "total_buildings": 11,
        "total_floors": 100,
        "total_locations": 50,
        "total_qrcodes": 25
    }

@router.get("/locations")
async def get_locations():
    """รายการจุดนำทางทั้งหมด"""
    return {"locations": [], "message": "Use Map Editor to add locations"}
