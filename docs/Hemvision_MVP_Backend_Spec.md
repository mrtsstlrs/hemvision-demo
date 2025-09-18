# ТЗ для Backend (MVP) — Hemvision

## 1. Область работ
Реализовать **Core API** и **Inference API** как два независимых сервиса. Обеспечить: аутентификацию, управление организациями/классами/медиа, запуск инференса изображений и видео (сэмплинг), хранение детекций, формирование «Анализов», экспорт CSV, шаринг по токен-ссылкам с TTL, простой аудит-лог. Хранилища: Postgres + MinIO (S3).

## 2. Технологии
- Python 3.11, FastAPI/uvicorn, Pydantic v2, SQLAlchemy 2.x, Alembic.
- Postgres 16 (расширения: `uuid-ossp`, `citext`).
- MinIO (S3-совместимое), `boto3`/`minio` SDK.
- Inference: FastAPI + ONNX Runtime (CPU; опционально OpenVINO EP), OpenCV/ffmpeg для кадров.
- Пароли: Argon2; токены: JWT (HS256).

## 3. Сервисная компоновка
- **core-api** (порт 8080): доменная логика, БД, presigned URLs, аудит, CSV.
- **inference** (порт 8090): приём `s3_key`, извлечение пикселей, resize/letterbox, прогон YOLOv11.onnx, NMS, выдача детекций (в slug).
- Общение: Core → Inference по HTTP (internal). Mapping `class_slug → class_id` — в Core.

## 4. Переменные окружения (мин. набор)
**core-api**
```
DATABASE_URL=postgresql+psycopg://user:pass@postgres:5432/hemvision
S3_ENDPOINT=http://minio:9000
S3_REGION=us-east-1
S3_ACCESS_KEY=...
S3_SECRET_KEY=...
S3_BUCKET=hemvision-media
JWT_SECRET=change-me
JWT_EXPIRES_MIN=43200   # 30 дней
BASE_SHARE_URL=https://app.hemvision.local/s/
MAX_UPLOAD_MB=20
```
**inference**
```
S3_ENDPOINT=...
S3_BUCKET=hemvision-media
S3_ACCESS_KEY=...
S3_SECRET_KEY=...
YOLO_ONNX_PATH=/models/yolov11.onnx
INPUT_SIZE=640
CONF_TH=0.25
IOU_TH=0.50
DEFAULT_SAMPLE_FPS=1
DEFAULT_MAX_FRAMES=10
```

## 5. Модель данных (БД) — кратко
Таблицы: `users, organizations, memberships(role: org_admin|member), classes(global/org), media_assets(type:image|video), detections, analyses, analysis_items, share_links(scope: analysis|media), audit_logs`.  
Ключевые индексы:
- `media_assets(org_id, type, created_at)`
- `detections(media_id)`, `detections(media_id, frame_index)`
- `share_links(token)`
- `audit_logs(org_id, created_at)`
Seed: глобальные классы `{neutrophil, lymphocyte, monocyte, eosinophil, basophil, blast}`.

Миграции Alembic:
- `001_init` — схемы и типы.
- `002_seed_global_classes` — сид.
- (опц.) `003_indexes` — дополнительные индексы.

## 6. RBAC и безопасность
- JWT Bearer в заголовке `Authorization: Bearer <token>`.
- `OrgAdmin`: CRUD по участникам, классам; видит аудит организации.
- `Member/Individual`: доступ к своим данным и данным своей организации.
- `Viewer`: публичные руты `/share/{token}` без JWT.
- Ограничение загрузки по размеру — на уровне presigned и Nginx.

## 7. Поток загрузки медиа (обязателен)
1) `POST /media` (Core) — регистрируем объект (метаданные), выдаём presigned PUT.
2) Клиент грузит файл в MinIO по presigned URL.
3) `POST /media/{id}/commit` (Core) — помечаем как загруженный (или `HEAD` в MinIO с проверкой размеров). (Можно объединить в `POST /media` + webhook, но для MVP — явный commit.)
4) (опц.) генерируем thumbnail (backend-задача синхронно для изображений).

## 8. Inference контракт (Core ↔ Inference)
**Core → Inference** `POST /infer`:
```json
{
  "s3_key": "org-<id>/user-<id>/media-<uuid>.mp4",
  "type": "video",
  "params": {
    "input_size": 640,
    "conf_th": 0.25,
    "iou_th": 0.5,
    "sample_fps": 1,
    "max_frames": 10
  }
}
```
**Inference → Core (ответ)**:
```json
{
  "detections": [
    {"frame_index":0,"frame_ts_ms":0,"x":123,"y":64,"w":58,"h":58,"score":0.91,"class_slug":"neutrophil"},
    {"frame_index":null,"x":10,"y":20,"w":30,"h":40,"score":0.88,"class_slug":"lymphocyte"}
  ],
  "metrics": {"num_frames": 10, "avg_ms_per_frame": 75}
}
```
Требования:
- Для изображений `frame_index=null`.
- Сервис Inference не знает про IDs классов: только `class_slug`.
- Core маппит `slug → class_id`, создаёт `detections (orig_class_id, class_id=orig)`.
- Поведение `overwrite` (перезапись детекций по media_id): параметр запроса к Core.

## 9. REST API (Core) — описание эндпоинтов

### Auth
- `POST /auth/register`  
  Вход: `{email, password, full_name?}`.  
  Выход: `201`, `{id, email}`.  
- `POST /auth/login`  
  Вход: `{email, password}`. Выход: `{access_token, token_type="bearer", expires_in}`.

### Organizations & Members
- `POST /orgs` (JWT) → создать организацию, автор — OrgAdmin.  
- `GET /orgs/me` → список организаций пользователя (для выбора контекста).  
- `POST /orgs/{org_id}/members` → добавить участника (email, role). (MVP: без отправки инвайтов; если email не существует — 400 или auto-create с временным паролем флагом — решаем просто: 400.)
- `GET /orgs/{org_id}/members` → список членов.

### Classes
- `GET /classes?scope=all|global|org` → объединённый список с пометкой `is_global`.  
- `POST /classes` (org-scoped) → `{name}` (slug генерится сервером, уникален в рамках org).  
- `PATCH /classes/{id}` → `{name?}`. (Удаление в MVP — запретить, либо soft-disable.)

### Media
- `POST /media`  
  Вход:
  ```json
  {
    "org_id": "<uuid>|null", "type": "image|video",
    "filename":"IMG_001.png","bytes":1234567,"width":2048,"height":1536,
    "metadata": {"stain":"...", "magnification":"...", "device":"...", "um_per_px":0.1}
  }
  ```
  Выход: `201 {media_id, s3_key, presigned_put_url, presigned_put_headers}`.
- `POST /media/{id}/commit` → проверяем наличие объекта в S3; ставим флаг `uploaded=true`.  
- `GET /media/{id}` → карточка, presigned GET для просмотра (короткий TTL, напр. 5 мин).  
- `DELETE /media/{id}` → удалить (каскадно удалит `detections`, `analysis_items`).

### Inference
- `POST /inference`  
  Query: `media_id`, `sample_fps?` (def=1), `max_frames?` (def=10), `overwrite?` (def=true).  
  Действия: валидация media, запрос к Inference, маппинг slug→class_id, запись `detections`.  
  Ответ: `{counts_per_class: [{"class_id":"...","class_name":"...","count":N}], "frames":K}`.

### Detections
- `GET /media/{id}/detections?frame_index?` → список детекций (пагинация не нужна).  
- `PATCH /detections/{det_id}`  
  Вход: `{class_id}` → обновляет `class_id`, `corrected_by = user_id`.

### Analyses
- `POST /analyses` → `{title, org_id?}` (org_id=контекст или null для Individual).  
- `POST /analyses/{id}/items` → `{media_ids: []}` (batch add).  
- `GET /analyses/{id}` → карточка + список media (id, filename, thumb_url).  
- `GET /analyses/{id}/summary` → агрегат по текущему `class_id`:
  ```json
  [{"class_id":"...","class_name":"Neutrophil","count":123}, ...]
  ```
- `GET /analyses/{id}/export.csv?details=0|1`  
  `details=0` → `class_name,count`  
  `details=1` → `media_id,filename,frame_index,x,y,w,h,score,orig_class,class`

### Sharing (public)
- `POST /share`  
  Вход: `{scope_type:"analysis|media", scope_id:"<uuid>", expires_in_hours:null|int}`  
  Выход: `{token, url: BASE_SHARE_URL + token, expires_at|null}`.
- `GET /share/{token}` (без JWT)  
  Возвращает read-only данные:  
  - для `analysis`: summary + список медиа (presigned GET на просмотр), без приватных метаданных;  
  - для `media`: детекции, presigned GET, базовые метаданные.  
  Истёкший токен → 404.

### Audit
- `GET /audit?org_id=...&limit=...` (OrgAdmin) — последние записи.

## 10. Валидации и ограничения
- Медиа: `bytes ≤ MAX_UPLOAD_MB*1024*1024`, `type in {image,video}`.  
- Видео: поддерживаемое содержимое — MP4/H.264 (референс), AVI — best effort.  
- Классы: `name` длина 2..64, `slug` генерируется (latin, `-`/`_`), уникален в org.  
- Detections: `x,y,w,h` — целые, внутри габаритов (core может не строго валидировать, но нормализует в UI).

## 11. Аудит-события (поле `action`)
- `user.login`  
- `media.upload_init`, `media.upload_commit`  
- `inference.run` (data: `{media_id, frames, avg_ms_per_frame}`)  
- `detection.edited` (data: `{det_id, from, to}`)  
- `analysis.created`, `analysis.items_added`  
- `analysis.export_csv`  
- `share.created`, `share.viewed`

## 12. Ошибки (HTTP и коды)
- 400 — невалидные параметры/метаданные; неподдерживаемый тип файла/видео.  
- 401 — неавторизован.  
- 403 — нет прав (org scope / чужие данные).  
- 404 — не найдено (включая share token истёк/не существует).  
- 409 — конфликт (`class` slug уже существует в org; повторная commit без overwrite).  
- 413 — файл слишком большой.  
- 502 — ошибка Inference (нет модели/не удалось декодировать видео).  
Тело ошибки: `{code:"string", message:"human readable", details?:{...}}`.

## 13. Производительность и SLA
- Цель: `image inference ≤ 1s` на референс-CPU при `INPUT_SIZE=640`.  
- Видео: до 10 кадров → суммарно ≤ 10× image; ответ может содержать `metrics`.  
- Presigned GET/PUT TTL: PUT ~15 мин, GET ~5 мин.  
- Индексация для выборок суммарных подсчётов по analysis.

## 14. Логи, мониторинг, трассировка
- Структурированные JSON-логи (`request_id`, `user_id`, `org_id`).  
- Метрики (опц.) через `/metrics` (Prometheus) — не критично в MVP.  
- Корреляция Core↔Inference по `request_id` в заголовке `X-Request-ID`.

## 15. Тестирование
- Unit: схемы, валидация, сервисы классов/детекций.  
- Интеграционные: presigned upload (MinIO), инференс мок/реальный onnx, CSV экспорт.  
- E2E: happy-path сценарии (загрузка → инференс → правка → анализ → экспорт → шаринг).

## 16. Документация
- Автогенерируемый OpenAPI (Swagger UI на `/docs`, ReDoc на `/redoc`).  
- Примеры запросов/ответов по ключевым ручкам.  
- README по переменным окружения и процедуре миграций (Alembic).

## 17. Деплой
- Docker images: `hemvision-core:<ver>`, `hemvision-infer:<ver>`.  
- Docker Compose файл с сервисами: postgres, minio, core-api, inference, nginx, init-bucket.  
- Скрипт `alembic upgrade head` при старте core-api.  
- Seed глобальных классов выполнится один раз (идемпотентно).
