# backend/api/detect.py

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse, Response
from tempfile import NamedTemporaryFile
import os
import logging

from services.inference import InferenceService
from depends import get_inference_service, get_settings

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/detect")
async def detect(
    file: UploadFile = File(...),
    settings = Depends(get_settings),
    inference_service: InferenceService = Depends(get_inference_service),
):
    """
    Загрузка изображения или видео, возвращает аннотированный файл.
    """
    contents = await file.read()
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(contents) > max_bytes:
        logger.warning(f"Upload too large: {len(contents)} bytes")
        raise HTTPException(status_code=413, detail="File too large")

    suffix = os.path.splitext(file.filename)[1].lower()
    with NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(contents)
        tmp_path = tmp.name

    try:
        if suffix in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
            # предсказание изображения, возвращаем JPEG-байты
            out_bytes = inference_service.predict_image(tmp_path)
            return Response(content=out_bytes, media_type='image/jpeg')
        elif suffix in ['.mp4', '.avi', '.mkv']:
            # предсказание видео, возвращаем готовый файл
            processed = inference_service.predict_video(tmp_path)
            if not processed:
                raise HTTPException(status_code=500, detail="Video processing failed")
            return FileResponse(
                path=processed,
                media_type='video/mp4',
                filename=os.path.basename(processed)
            )
        else:
            raise HTTPException(status_code=415, detail="Unsupported file type")
    finally:
        try:
            os.unlink(tmp_path)
        except:
            pass
