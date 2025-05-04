import axios from 'axios';

const API = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  responseType: 'blob'
});

export async function uploadFile(file, onUploadProgress) {
  const data = new FormData();
  data.append('file', file);
  const res = await API.post('/detect', data, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress
  });
  // Берём content-type из заголовков и создаём Blob с ним
  const contentType = res.headers['content-type'] || res.data.type || 'video/mp4';
  return new Blob([res.data], { type: contentType });
}
