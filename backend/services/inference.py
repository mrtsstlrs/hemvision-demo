# backend/services/inference.py

from ultralytics import RTDETR
import cv2
import tempfile
import os
import shutil
import subprocess

class InferenceService:
    def __init__(self, model_path: str, conf_threshold: float = 0.25, imgsz: int = 640):
        self.model = RTDETR(model_path)
        self.model.model.cpu().eval()
        self.conf_threshold = conf_threshold
        self.imgsz = imgsz

    def predict_image(self, img_path: str) -> bytes:
        results = self.model.predict(
            source=img_path,
            conf=self.conf_threshold,
            imgsz=self.imgsz,
            save=False,
            stream=False
        )
        annotated = results[0].plot()
        ret, buf = cv2.imencode('.jpg', annotated)
        return buf.tobytes()

    def predict_video(self, vid_path: str) -> str:
        """
        Делаем инференс, сохраняем аннотированное видео во временную папку,
        затем конвертируем его в MP4 (H.264) и возвращаем путь к MP4.
        """
        tmpdir = tempfile.mkdtemp(prefix='rt_detr_')
        # 1) Сохраняем аннотированное видео (может получиться AVI/MJPG)
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

        # 2) Найдём первый видеофайл в tmpdir
        src_video = None
        for root, _, files in os.walk(tmpdir):
            for f in files:
                if f.lower().endswith(('.mp4', '.avi', '.mkv')):
                    src_video = os.path.join(root, f)
                    break
            if src_video:
                break
        if not src_video:
            raise RuntimeError(f"No video file found in {tmpdir}")

        # 3) Конвертируем в MP4 + H.264
        dst_mp4 = os.path.join(tmpdir, "result.mp4")
        # '-y' перезаписать без вопросов
        subprocess.run([
            "ffmpeg", "-y", "-i", src_video,
            "-c:v", "libx264", "-preset", "veryfast",
            "-c:a", "aac", "-movflags", "+faststart",
            dst_mp4
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # 4) Удаляем исходное (AVI/MKV) чтобы не засорять tmpdir
        if src_video != dst_mp4:
            os.remove(src_video)

        return dst_mp4