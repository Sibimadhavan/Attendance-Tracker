# Attendance Tracking System

A full-stack attendance tracking application with user authentication, email verification, and calendar view.

## Tech Stack

- **Backend**: Python FastAPI
- **Frontend**: React with Vite
- **Database**: MongoDB
- **Cache/Session**: Redis
- **Container**: Docker

## Features

- User registration with email verification
- Password hashing (bcrypt)
- Token-based session management (Redis)
- Clock in/out functionality
- Attendance history view
- Calendar view with attendance status
- All users' attendance overview

## Setup

### Prerequisites

- Docker installed on your system
- Gmail account with App Password (for email verification)

### Configure Email

1. Go to Google Account settings
2. Enable 2-Step Verification
3. Generate an App Password: Account > Security > App Passwords
4. Update `backend/.env` with your credentials:

```env
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### Run with Docker

```bash
docker-compose up --build
```

Access the application at: `http://localhost`

API endpoints: `http://localhost:8000/api`

### Development (without Docker)

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Update `frontend/src/services/api.js` baseURL to `http://localhost:8000/api` for local dev.

## API Endpoints

### Auth
- `POST /api/auth/register` - Register new user
- `POST /api/auth/verify` - Verify email
- `POST /api/auth/login` - Login
- `POST /api/auth/logout` - Logout

### Attendance
- `POST /api/attendance/check-in` - Mark attendance
- `POST /api/attendance/check-out` - Mark logout
- `GET /api/attendance/today` - Today's status
- `GET /api/attendance/my` - My attendance history
- `GET /api/attendance/all` - All users' attendance
- `GET /api/attendance/calendar` - Calendar view

## Collections

### users
- user_id (UUID)
- name
- email
- password (hashed)
- is_verified
- created_at
- updated_at

### attendance
- attendance_id (UUID)
- user_id
- date (YYYY-MM-DD)
- check_in (ISO datetime)
- check_out (ISO datetime)
- status (present/absent)
- created_at

Used rate limiting 
Summary of what was added:
     
  ┌────────────────────┬─────────────┬────────┬────────────────────────────────────────┐
  │      Endpoint      │    Limit    │ Window │                  Why                   │
  ├────────────────────┼─────────────┼────────┼────────────────────────────────────────┤
  │ /api/auth/login    │ 5 requests  │ 60 sec │ Prevents brute-force password guessing │
  ├────────────────────┼─────────────┼────────┼────────────────────────────────────────┤
  │ /api/auth/register │ 3 requests  │ 60 sec │ Prevents spam account creation         │
  ├────────────────────┼─────────────┼────────┼────────────────────────────────────────┤
  │ /api/auth/verify   │ 10 requests │ 60 sec │ Prevents token brute-forcing           │
  └────────────────────┴─────────────┴────────┴────────────────────────────────────────┘
  It uses Redis to track request counts per IP per endpoint, and auto-expires after the
  window. No extra libraries needed — uses the Redis already in the stack.