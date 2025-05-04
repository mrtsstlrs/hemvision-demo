import React from 'react';

export default function PreviewCanvas({ blob }) {
  const url = URL.createObjectURL(blob);
  const isVideo = blob.type.startsWith('video/');

  if (isVideo) {
    return (
      <div className="mt-6 text-center">
        <video controls className="max-w-full rounded-lg shadow">
          <source src={url} type={blob.type} />
          Ваш браузер не поддерживает видео.
        </video>
      </div>
    );
  } else {
    return (
      <div className="mt-6 text-center">
        <img src={url} alt="Result" className="max-w-full rounded-lg shadow" />
      </div>
    );
  }
}
