// frontend/src/components/UploadCard.jsx

import React, { useRef } from 'react';

export default function UploadCard({ onFileSelect, uploading, progress }) {
  const dropRef = useRef(null);
  const inputRef = useRef(null);

  const handleDragOver = e => {
    e.preventDefault();
    dropRef.current.classList.add('drag-over');
  };

  const handleDragLeave = e => {
    e.preventDefault();
    dropRef.current.classList.remove('drag-over');
  };

  const handleDrop = e => {
    e.preventDefault();
    dropRef.current.classList.remove('drag-over');
    const file = e.dataTransfer.files[0];
    if (file) onFileSelect(file);
  };

  return (
    <div className="upload-card">
      <h2>Загрузить изображение или видео</h2>

      <div
        ref={dropRef}
        className="upload-zone"
        onClick={() => inputRef.current && inputRef.current.click()}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        {/* Скрытое поле выбора файла */}
        <input
          ref={inputRef}
          type="file"
          accept="image/*,video/*"
          style={{ display: 'none' }}
          onChange={e => e.target.files[0] && onFileSelect(e.target.files[0])}
        />

        <div className="upload-content">
          <svg
            width="48"
            height="48"
            fill="none"
            stroke="var(--color-accent)"
            strokeWidth="2"
            viewBox="0 0 24 24"
          >
            <path d="M12 5v14m7-7H5" />
          </svg>
          <p>Перетащите файл сюда или кликните для выбора</p>
        </div>
      </div>

      <button className="upload-button" disabled={uploading}>
        {uploading ? `Загружаем… ${progress}%` : 'Загрузить'}
      </button>
    </div>
  );
}
