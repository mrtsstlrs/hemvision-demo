// frontend/src/components/PreviewCanvas.jsx

import React from 'react';

export default function PreviewCanvas({ blob }) {
  const url = URL.createObjectURL(blob);
  const isVideo = blob.type.startsWith('video/');

  return (
    <div className="result-container">
      <h2 className="result-title">Результат</h2>
      {isVideo ? (
        <video
          controls
          preload="metadata"
          className="result-media"
        >
          <source src={url} type={blob.type} />
          Ваш браузер не поддерживает видео.
        </video>
      ) : (
        <img
          src={url}
          alt="Результат"
          className="result-media"
        />
      )}
    </div>
  );
}
