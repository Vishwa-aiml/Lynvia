import axios from 'axios';
import { auth } from '../config/firebase';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to attach Firebase ID Token
apiClient.interceptors.request.use(
  async (config) => {
    const user = auth.currentUser;
    if (user) {
      try {
        // Force refresh if token is close to expiry or just get the current token
        const token = await user.getIdToken();
        config.headers.Authorization = `Bearer ${token}`;
      } catch (error) {
        console.error("Error getting Firebase token", error);
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle global errors (e.g., 401 Unauthorized)
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      if (error.response.status === 401) {
        // The backend rejected the token or token was missing.
        // In a real app, you might trigger a logout or a redirect to /login here.
        console.warn('Unauthorized access. Please login again.');
      } else if (error.response.status === 403) {
        console.warn('Forbidden access.');
      } else if (error.response.status >= 500) {
        console.error('Server error', error.response.data);
      }
    } else if (error.request) {
      // The request was made but no response was received
      console.error('Network Error: Make sure the backend is running.');
    }
    return Promise.reject(error);
  }
);

export default apiClient;
