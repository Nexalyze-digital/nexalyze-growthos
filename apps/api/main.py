from time import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, brands, content, health, publishing, research
from app.core.config import settings
from app.db import init_db

app = FastAPI(title=settings.app_name, version=settings.version)
init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Workspace-Id"],
)

app.include_router(health.router)
app.include_router(auth.router, prefix="/api/v1")
app.include_router(brands.router, prefix="/api/v1")
app.include_router(content.router, prefix="/api/v1")
app.include_router(research.router, prefix="/api/v1")
app.include_router(publishing.router, prefix="/api/v1")

_auth_attempts: dict[str, list[float]] = {}


@app.middleware("http")
async def security_middleware(request: Request, call_next):
    if request.url.path in {"/api/v1/auth/login", "/api/v1/auth/register"}:
        key = request.client.host if request.client else "unknown"
        now = time()
        window = now - 60
        attempts = [stamp for stamp in _auth_attempts.get(key, []) if stamp >= window]
        if len(attempts) >= settings.auth_rate_limit_per_minute:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many authentication attempts. Try again later."},
            )
        attempts.append(now)
        _auth_attempts[key] = attempts

    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    return response
