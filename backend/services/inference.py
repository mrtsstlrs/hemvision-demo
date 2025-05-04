# backend/services/inference.py

from ultralytics import RTDETR
import cv2
import tempfile
import os
import shutil

class InferenceService:
    def __init__(self, model_path: str, conf_threshold: float = 0.25, imgsz: int = 640):
        # Загрузка RTDETR-модели на CPU и перевод в eval
        self.model = RTDETR(model_path)
        self.model.model.cpu().eval()
        self.conf_threshold = conf_threshold
        self.imgsz = imgsz

    def predict_image(self, img_path: str) -> bytes:
        """
        Инференс на изображении, возвращает JPEG-байты с аннотацией.
        """
        results = self.model.predict(
            source=img_path,
            conf=self.conf_threshold,
            imgsz=self.imgsz,
            save=False,
            stream=False
        )
        annotated = results[0].plot()  # numpy array, BGR
        ret, buf = cv2.imencode('.jpg', annotated)
        return buf.tobytes()

    def predict_video(self, vid_path: str) -> str:
        """
        Инференс на видео, сохраняет аннотированный файл во временную папку и возвращает путь.
        Удаляет папку 'runs' после сохранения.
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

        # Удаляем стандартную папку runs/, если она была создана
        runs_dir = os.path.join(os.getcwd(), 'runs')
        if os.path.isdir(runs_dir):
            shutil.rmtree(runs_dir, ignore_errors=True)

        # Ищем файл .mp4/.avi/.mkv в tmpdir
        for root, _, files in os.walk(tmpdir):
            for f in files:
                if f.lower().endswith(('.mp4', '.avi', '.mkv')):
                    return os.path.join(root, f)

        raise RuntimeError(f"No video file found in {tmpdir}")
