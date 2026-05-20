from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from starlette.responses import JSONResponse
from app.database import redis_client

RATE_LIMITS = {
    "/api/auth/login": {"max": 5, "window": 60},
    "/api/auth/register": {"max": 3, "window": 60},
    "/api/auth/verify": {"max": 10, "window": 60},
}


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        if path in RATE_LIMITS:
            client_ip = request.client.host
            limit_key = f"rate:{path}:{client_ip}"
            config = RATE_LIMITS[path]
            max_requests = config["max"]
            window = config["window"]

            current = await redis_client.get(limit_key)
            if current is None:
                await redis_client.setex(limit_key, window, "1")
            elif int(current) >= max_requests:
                ttl = await redis_client.ttl(limit_key)
                return JSONResponse(
                    status_code=429,
                    content={"detail": f"Too many requests. Try again in {ttl} seconds."},
                )
            else:
                await redis_client.incr(limit_key)

        response = await call_next(request)
        return response
