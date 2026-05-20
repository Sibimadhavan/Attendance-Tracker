import re
from fastapi import APIRouter, HTTPException, status, Depends, Query
from datetime import datetime, date
from pydantic import BaseModel
from typing import Optional
from app.database import db, redis_client
from app.utils.auth import generate_uuid
from app.utils.dependencies import get_current_user

router = APIRouter()

MAX_RECORDS = 366


def validate_month(month: str) -> bool:
    return bool(re.match(r"^\d{4}-(0[1-9]|1[0-2])$", month))


def validate_date(date_str: str) -> bool:
    return bool(re.match(r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$", date_str))


class CheckInResponse(BaseModel):
    message: str
    attendance_id: str
    check_in: str
    date: str


class CheckOutResponse(BaseModel):
    message: str
    check_out: str


class AttendanceRecord(BaseModel):
    user_id: str
    name: str
    email: str
    date: str
    check_in: Optional[str] = None
    check_out: Optional[str] = None
    status: str


@router.post("/check-in")
async def check_in(user_id: str = Depends(get_current_user)):
    today = date.today().isoformat()

    existing = await db.attendance.find_one({"user_id": user_id, "date": today})
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already checked in for today")

    now = datetime.utcnow().isoformat()
    attendance_id = generate_uuid()

    await db.attendance.insert_one({
        "attendance_id": attendance_id,
        "user_id": user_id,
        "date": today,
        "check_in": now,
        "check_out": None,
        "status": "present",
        "created_at": datetime.utcnow(),
    })

    return {"message": "Checked in successfully", "attendance_id": attendance_id, "check_in": now, "date": today}


@router.post("/check-out")
async def check_out(user_id: str = Depends(get_current_user)):
    today = date.today().isoformat()

    record = await db.attendance.find_one({"user_id": user_id, "date": today})
    if not record:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No check-in found for today")

    if record["check_out"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already checked out for today")

    now = datetime.utcnow().isoformat()
    await db.attendance.update_one(
        {"user_id": user_id, "date": today},
        {"$set": {"check_out": now, "updated_at": datetime.utcnow()}}
    )

    return {"message": "Checked out successfully", "check_out": now}


@router.get("/today")
async def get_today_status(user_id: str = Depends(get_current_user)):
    today = date.today().isoformat()

    record = await db.attendance.find_one({"user_id": user_id, "date": today})
    if not record:
        return {"date": today, "status": "absent", "check_in": None, "check_out": None}

    return {
        "attendance_id": record["attendance_id"],
        "date": record["date"],
        "check_in": record.get("check_in"),
        "check_out": record.get("check_out"),
        "status": record["status"],
    }


@router.get("/my")
async def get_my_attendance(
    user_id: str = Depends(get_current_user),
    month: Optional[str] = Query(None, description="Format: YYYY-MM"),
):
    query = {"user_id": user_id}
    if month:
        if not validate_month(month):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid month format. Use YYYY-MM")
        query["date"] = {"$regex": f"^{month}"}

    cursor = db.attendance.find(query).sort("date", -1)
    records = await cursor.to_list(length=MAX_RECORDS)

    return {"records": records, "count": len(records)}


@router.get("/all")
async def get_all_attendance(
    user_id: str = Depends(get_current_user),
    date_filter: Optional[str] = Query(None, description="Format: YYYY-MM-DD"),
    month: Optional[str] = Query(None, description="Format: YYYY-MM"),
):
    query = {}
    if date_filter:
        if not validate_date(date_filter):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid date format. Use YYYY-MM-DD")
        query["date"] = date_filter
    elif month:
        if not validate_month(month):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid month format. Use YYYY-MM")
        query["date"] = {"$regex": f"^{month}"}

    cursor = db.attendance.find(query).sort("date", -1)
    records = await cursor.to_list(length=MAX_RECORDS)

    result = []
    for record in records:
        user = await db.users.find_one({"user_id": record["user_id"]})
        result.append({
            "user_id": record["user_id"],
            "name": user["name"] if user else "Unknown",
            "email": user["email"] if user else "Unknown",
            "date": record["date"],
            "check_in": record.get("check_in"),
            "check_out": record.get("check_out"),
            "status": record["status"],
        })

    return {"records": result, "count": len(result)}


@router.get("/calendar")
async def get_calendar_data(
    user_id: str = Depends(get_current_user),
    month: str = Query(..., description="Format: YYYY-MM"),
):
    if not validate_month(month):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid month format. Use YYYY-MM")

    year, mon = month.split("-")
    next_month = str(int(mon) + 1).zfill(2) if int(mon) < 12 else "01"
    next_year = str(int(year) + 1) if int(mon) == 12 else year
    start = f"{month}-01"
    end_pattern = f"{next_year}-{next_month}"

    query = {
        "user_id": user_id,
        "date": {"$gte": start, "$lt": end_pattern}
    }

    cursor = db.attendance.find(query).sort("date", 1)
    records = await cursor.to_list(length=MAX_RECORDS)

    calendar_data = {}
    for record in records:
        calendar_data[record["date"]] = {
            "status": record["status"],
            "check_in": record.get("check_in"),
            "check_out": record.get("check_out"),
        }

    return {"month": month, "data": calendar_data}
