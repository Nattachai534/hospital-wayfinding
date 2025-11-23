from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db

router = APIRouter(prefix="/api/navigation", tags=["navigation"])

@router.get("/buildings")
async def get_buildings():
    """รายการอาคารทั้งหมด"""
    buildings = [
        {"code": "A", "name": "อาคารทศมินทราธิราช", "floors": 25, "type": "main"},
        {"code": "B", "name": "ตึกสิรินธร", "floors": 18, "type": "ipd"},
        {"code": "CHALERM", "name": "อาคารเฉลิมพระเกียรติฯ", "floors": 12, "type": "opd"},
        {"code": "D", "name": "ตึกอำนวยการ", "floors": 5, "type": "admin"},
        {"code": "E", "name": "ตึกอุบัติเหตุและฉุกเฉิน", "floors": 4, "type": "er"},
        {"code": "F", "name": "ตึกอายุรกรรม", "floors": 6, "type": "ipd"},
        {"code": "G", "name": "ตึกสอาด ศิริพัฒน์", "floors": 8, "type": "heart"},
        {"code": "H", "name": "ตึกหลวงชำนาญเนติศาสตร์", "floors": 6, "type": "clinic"},
        {"code": "I", "name": "ตึกเจริญ พูลวรลักษณ์", "floors": 5, "type": "other"},
        {"code": "J", "name": "ตึกวิเคราะห์โรคหัวใจ", "floors": 4, "type": "heart"},
        {"code": "K", "name": "ตึกวาศอุทิศ", "floors": 3, "type": "ems"}
    ]
    return {"buildings": buildings}

@router.get("/rooms/{building}/{floor}")
async def get_rooms(building: str, floor: str):
    """รายการห้องในแต่ละชั้น"""
    rooms_data = {
        "CHALERM": {
            "9": [
                {"code": "SC", "name": "ห้องประชุม SC", "type": "conference"},
                {"code": "VC1", "name": "ห้องประชุม VC1", "type": "conference"},
                {"code": "VC2", "name": "ห้องประชุม VC2", "type": "conference"},
                {"code": "VC3", "name": "ห้องประชุม VC3", "type": "conference"},
                {"code": "MED_RECORD", "name": "ห้องขอประวัติการรักษา", "type": "service"}
            ],
            "11": [
                {"code": "YOTHI", "name": "ห้องประชุมโยธี", "type": "conference"},
                {"code": "RATCHAPHRUEK", "name": "ห้องประชุมราชพฤกษ์", "type": "conference"},
                {"code": "SUPHANNIKA", "name": "ห้องประชุมสุพรรณิการ์", "type": "conference"},
                {"code": "PHAYATHAI", "name": "ห้องประชุมพญาไท", "type": "conference"},
                {"code": "PARICHAT", "name": "ห้องประชุมปาริชาติ", "type": "conference"},
                {"code": "VIP_ROOM", "name": "ห้องรับรองวิทยากร", "type": "vip"}
            ],
            "12": [
                {"code": "PHIBUN", "name": "ห้องประชุมพิบูลสงคราม", "type": "conference"}
            ]
        },
        "E": {
            "1": [{"code": "ER", "name": "ห้องฉุกเฉิน", "type": "emergency"}],
            "4": [{"code": "EMS_CONF", "name": "ห้องประชุม EMS", "type": "conference"}]
        }
    }
    
    rooms = rooms_data.get(building, {}).get(floor, [])
    return {"building": building, "floor": floor, "rooms": rooms}

@router.get("/route")
async def get_route(from_building: str = "A", from_floor: str = "1", 
                   to_building: str = "CHALERM", to_floor: str = "11", to_room: str = ""):
    """คำนวณเส้นทาง"""
    steps = [
        {"step": 1, "instruction": f"เดินจากจุดปัจจุบันไปยัง{to_building}", "distance": 50},
        {"step": 2, "instruction": "เข้าประตูหลักของอาคาร", "distance": 10},
        {"step": 3, "instruction": "เดินไปยังโถงลิฟต์", "distance": 20},
        {"step": 4, "instruction": f"ขึ้นลิฟต์ไปชั้น {to_floor}", "distance": 0},
        {"step": 5, "instruction": "ออกจากลิฟต์ตามป้ายบอกทาง", "distance": 15},
        {"step": 6, "instruction": f"ถึง {to_room} แล้ว", "distance": 0}
    ]
    
    total_distance = sum(s["distance"] for s in steps)
    estimated_time = max(1, total_distance // 50)
    
    return {
        "from": {"building": from_building, "floor": from_floor},
        "to": {"building": to_building, "floor": to_floor, "room": to_room},
        "steps": steps,
        "total_distance": total_distance,
        "estimated_time": estimated_time
    }
