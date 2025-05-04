import logging

from fastapi import FastAPI, Depends
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
        title="HemVision Backend Service",
        version="1.0.0",
    )

    # Rate limiting
    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)
    # Обработчик берём из главного модуля slowapi
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Роуты
    app.include_router(detect_router, prefix="/api")

    return app

app = create_app()
