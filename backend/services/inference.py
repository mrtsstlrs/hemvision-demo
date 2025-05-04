# backend/services/inference.py

from ultralytics import RTDETR
import cv2
import tempfile
import os

class InferenceService:
    def __init__(self, model_path: str, conf_threshold: float = 0.25, imgsz: int = 640):
        # Загрузка модели (без передачи device)
        self.model = RTDETR(model_path)
        # Переводим PyTorch-модуль на CPU
        self.model.model.cpu().eval()
        self.conf_threshold = conf_threshold
        self.imgsz = imgsz

    def predict_image(self, img_path: str) -> bytes:
        """
        Предсказание на одном изображении.
        Возвращает байты JPEG-аннотации.
        """
        results = self.model.predict(
            source=img_path,
            conf=self.conf_threshold,
            imgsz=self.imgsz,
            save=False,
            stream=False
        )
        annotated = results[0].plot()  # numpy array BGR
        ret, buf = cv2.imencode('.jpg', annotated)
        return buf.tobytes()

    def predict_video(self, vid_path: str) -> str:
        """
        Инференс на видео, сохраняет аннотированный файл во временную папку и возвращает путь.
        """
        tmpdir = tempfile.mkdtemp(prefix='rt_detr_')
        # Сохраняем аннотированное видео прямо в tmpdir
        self.model.predict(
            source=vid_path,
            conf=self.conf_threshold,
            imgsz=self.imgsz,
            save=True,
            project=tmpdir,
            name='',
            exist_ok=True,
            stream=False
        )
        # Ищем файл .mp4/.avi/.mkv в tmpdir
        for root, _, files in os.walk(tmpdir):
            for f in files:
                if f.lower().endswith(('.mp4', '.avi', '.mkv')):
                    return os.path.join(root, f)
        raise RuntimeError(f"No video file found in {tmpdir}")
