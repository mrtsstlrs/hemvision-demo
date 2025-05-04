from functools import lru_cache

from fastapi import Depends
# from pydantic import BaseSettings

from services.inference import InferenceService

class Settings:
    model_path: str = 'last.pt'
    conf_threshold: float = 0.1
    imgsz: int = 640
    max_upload_size_mb: int = 100

@lru_cache()
def get_settings() -> Settings:
    return Settings()

@lru_cache()
def get_inference_service(
    settings: Settings = Depends(get_settings)
) -> InferenceService:
    return InferenceService(
        model_path=settings.model_path,
        conf_threshold=settings.conf_threshold,
        imgsz=settings.imgsz
    )
