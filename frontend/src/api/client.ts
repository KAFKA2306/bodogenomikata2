import axios from 'axios';
const getBaseUrl = () => {
    const envUrl = import.meta.env.VITE_API_BASE_URL;
    if (envUrl) return envUrl;
    if (typeof window !== 'undefined') {
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            return 'http://localhost:8000/api';
        }
        // Change to public backend endpoint if pages.dev deployment
        return 'https://bodogenomikata2.onrender.com/api';
    }
    return 'http://localhost:8000/api';
};
export const apiClient = axios.create({ baseURL: getBaseUrl(), headers: { 'Content-Type': 'application/json' } });
