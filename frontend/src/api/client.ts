import axios from 'axios';
const getBaseUrl = () => {
    const envUrl = import.meta.env.VITE_API_BASE_URL;
    if (envUrl) return envUrl;
    if (window.location.hostname === 'localhost') return 'http://localhost:8000/api';
    throw new Error('VITE_API_BASE_URL is not set. Please set it in your hosting platform.');
};
export const apiClient = axios.create({ baseURL: getBaseUrl(), headers: { 'Content-Type': 'application/json' } });
