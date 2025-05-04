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
    contents = await file.read()
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(contents) > max_bytes:
        raise HTTPException(413, "File too large")

    suffix = os.path.splitext(file.filename)[1].lower()
    with NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(contents)
        tmp_path = tmp.name

    try:
        if suffix in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
            img_bytes = inference_service.predict_image(tmp_path)
            return Response(content=img_bytes, media_type='image/jpeg')

        elif suffix in ['.mp4', '.avi', '.mkv']:
            video_path = inference_service.predict_video(tmp_path)
            filename = os.path.basename(video_path)
            headers = {"Content-Disposition": f'inline; filename="{filename}"'}
            # Добавляем Accept-Ranges, чтобы видео могло seek’иться
            return FileResponse(
                path=video_path,
                media_type='video/mp4',
                headers={**headers, "Accept-Ranges": "bytes"}
            )

        else:
            raise HTTPException(415, "Unsupported file type")
    finally:
        try:
            os.unlink(tmp_path)
        except:
            pass
