from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, attendance

app = FastAPI(title="Attendance Tracker")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(attendance.router, prefix="/api/attendance", tags=["Attendance"])


@app.get("/api/health")
async def health():
    return {"status": "ok"}
