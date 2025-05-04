# Hem Vision

<img src="frontend/public/logo.png" alt="Hem Vision Logo" width="150"/>

Сервис для детекции групп лейкоцитов на микроскопических изображениях и видео с помощью модели RT-DETR.
Позволяет загружать изображения и видео через удобный веб-интерфейс, обрабатывать их на CPU и получать результат с рамками и классами обнаруженных клеток.

---

## 🔍 Особенности

* **Модель детекции**: RT-DETR (Ultralytics) на CPU
* **Backend**: FastAPI + SlowAPI (rate-limit)
* **Frontend**: React + Vite, поддержка drag’n’drop, прогресс-бар, предпросмотр результата
* **Контейнеризация**: Docker & Docker Compose
* **Безопасность**: ограничение максимального размера загрузки (по умолчанию 100 МБ)
* **Простая интеграция**: готовые Docker Hub-образы для backend и frontend

---

## 📦 Сборка и запуск

### Требования

* Docker CE ≥ 20.10
* Docker Compose ≥ 1.29

### Запуск локально

1. Клонируйте репозиторий:

   ```bash
   git clone https://github.com/pumpsulp/hemvision.git
   cd hemvision
   ```
2. Запустите контейнеры:

   ```bash
   docker compose up
   ```
3. Перейдите:

   * **Backend API** → `http://localhost:8000/docs` (Swagger UI)
   * **Frontend UI**  → `http://localhost:3000`

---

## 🚀 Использование API

### POST `/api/detect`

* **Описание**: принимает файл (`image/*` или `video/*`), возвращает аннотированный результат
* **Параметр**: `file` (multipart-form)
* **Максимальный размер**: 100 МБ (конфигурируется)
* **Ответ**:

  * `image/jpeg` — аннотированное изображение
  * `video/mp4` — аннотированное видео (H.264, inline, поддержка seek)

Пример cURL:

```bash
curl -X POST http://localhost:8000/api/detect \
  -F "file=@/path/to/image.png" \
  --output result.jpg
```

---

## 🖥️ Frontend UI

* Загрузка drag’n’drop или по клику
* Индикация прогресса загрузки
* Автоматический предпросмотр изображения или видео
* Сине-голубая цветовая схема

Переменные окружения (в `docker-compose.yaml`):

```yaml
frontend:
  environment:
    VITE_API_URL: "http://localhost:8000/api"
```

---

## 🗂 Структура проекта

```
/
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py
│   ├── depends.py
│   ├── api/
│   │   └── detect.py
│   └── services/
│       └── inference.py
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   ├── public/
│   │   ├── favicon.ico
│   │   └── logo.png
│   └── src/
│       ├── index.jsx
│       ├── index.css
│       ├── App.jsx
│       └── components/
│           ├── UploadCard.jsx
│           ├── PreviewCanvas.jsx
│           └── Loader.jsx
├── docker-compose.yml
└── README.md
```

---


## 📝 Лицензия

Проект распространяется под лицензией [MIT](LICENSE).
