# backend/main.py

import logging

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from api.detect import router as detect_router
from depends import get_settings

def create_app() -> FastAPI:
    settings = get_settings()

    # Логирование
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("uvicorn")
    logger.setLevel(logging.INFO)

    app = FastAPI(
        title="Hemvision Backend Service",
        version="1.0.0",
    )

    # CORS — разрешаем запросы с фронтенда
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],            # или строго ваш домен, например ["http://localhost:3000"]
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

    # Rate limiting
    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Роуты
    app.include_router(detect_router, prefix="/api")

    return app

app = create_app()
