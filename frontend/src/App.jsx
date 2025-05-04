// frontend/src/App.jsx

import React, { useState } from 'react';
import UploadCard from './components/UploadCard';
import PreviewCanvas from './components/PreviewCanvas';
import Loader from './components/Loader';
import { uploadFile } from './services/api';

export default function App() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [resultBlob, setResultBlob] = useState(null);
  const [error, setError] = useState('');

  const handleFileSelect = async selected => {
    setFile(selected);
    setResultBlob(null);
    setError('');
    setProgress(0);
    setUploading(true);

    try {
      const blob = await uploadFile(selected, e =>
        setProgress(Math.round((e.loaded / e.total) * 100))
      );
      setResultBlob(blob);
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка при загрузке');
    } finally {
      setUploading(false);
    }
  };

  return (
    <>
      <header>
        <img src="./logo.png" alt="Hem Vision Logo" />
        <h1>Hem Vision</h1>
      </header>

      <main>
        <UploadCard
          onFileSelect={handleFileSelect}
          uploading={uploading}
          progress={progress}
        />

        {error && (
          <div className="mt-4 text-red-600 font-medium text-center">
            {error}
          </div>
        )}

        {resultBlob && <PreviewCanvas blob={resultBlob} />}
      </main>

      {uploading && <Loader />}
    </>
  );
}
