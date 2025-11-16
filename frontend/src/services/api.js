import axios from 'axios';

// API base URL - will be proxied by Vite in development
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Upload video file
export const uploadVideo = async (file, onProgress) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress: (progressEvent) => {
      if (onProgress && progressEvent.total) {
        const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        onProgress(progress);
      }
    },
  });

  return response.data;
};

// Get all jobs
export const getJobs = async () => {
  const response = await api.get('/jobs');
  return response.data;
};

// Get single job
export const getJob = async (jobId) => {
  const response = await api.get(`/jobs/${jobId}`);
  return response.data.job;
};

// Start clip generation
export const generateClips = async (jobId) => {
  const response = await api.post(`/jobs/${jobId}/generate`);
  return response.data;
};

// Get clips for a job
export const getClips = async (jobId) => {
  const response = await api.get(`/jobs/${jobId}/clips`);
  return response.data;
};

// Get single clip
export const getClip = async (jobId, clipId) => {
  const response = await api.get(`/jobs/${jobId}/clips/${clipId}`);
  return response.data;
};

// Trim clip
export const trimClip = async (jobId, clipId, startTime, endTime, aspectRatio) => {
  const response = await api.post(`/jobs/${jobId}/clips/${clipId}/trim`, {
    start_time: startTime,
    end_time: endTime,
    aspect_ratio: aspectRatio,
  });
  return response.data;
};

// Delete job
export const deleteJob = async (jobId) => {
  const response = await api.delete(`/jobs/${jobId}`);
  return response.data;
};

export default api;
