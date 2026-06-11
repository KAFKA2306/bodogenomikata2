import axios from 'axios';
const getBaseUrl = () => {
    const envUrl = import.meta.env.VITE_API_BASE_URL;
    if (envUrl) return envUrl;
    if (typeof window !== 'undefined') {
        // Fallback to absolute url if on localhost, else use relative /api
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            return 'http://localhost:8000/api';
        }
        return '/api';
    }
    return 'http://localhost:8000/api';
};
export const apiClient = axios.create({ baseURL: getBaseUrl(), headers: { 'Content-Type': 'application/json' } });
