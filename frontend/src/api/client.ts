import axios from 'axios';

// Automatically detect the API base URL. 
// If deployed, assume the backend is available at /api relative to the frontend, 
// or use the environment variable if configured.
const getBaseUrl = () => {
    if (import.meta.env.VITE_API_BASE_URL) return import.meta.env.VITE_API_BASE_URL;
    // Assume same domain (proxy) or a hardcoded production backend
    return window.location.hostname === 'localhost' ? 'http://localhost:8000/api' : 'https://bodogenomikata2-backend.onrender.com/api';
};

export const apiClient = axios.create({ 
    baseURL: getBaseUrl(), 
    headers: { 'Content-Type': 'application/json' } 
});
