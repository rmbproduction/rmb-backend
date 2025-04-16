import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Function to get CSRF token from cookie
const getCSRFToken = () => {
  const name = 'csrftoken';
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
};

// Create axios instance with base URL
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

// Add CSRF token to requests
api.interceptors.request.use((config) => {
  const csrfToken = getCSRFToken();
  if (csrfToken) {
    config.headers['X-CSRFToken'] = csrfToken;
  }
  
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Authentication endpoints
export const register = async (data) => {
  const response = await api.post('/accounts/signup/', data);
  return response.data;
};

export const login = async (data) => {
  const response = await api.post('/accounts/login/', data);
  return response.data;
};

// Request password reset (sends email)
export const requestPasswordReset = async (email) => {
  try {
    const response = await api.post('/api/accounts/password-reset/', {
      email: email.trim()
    });
    return response.data;
  } catch (error) {
    console.error('Password reset request error:', error.response?.data);
    throw error;
  }
};

// Reset password with token
export const resetPassword = async (token, password) => {
  try {
    const response = await api.post(`/api/accounts/reset-password/${token}/`, {
      password: password
    });
    return response.data;
  } catch (error) {
    console.error('Password reset error:', error.response?.data);
    throw error;
  }
};

export const logout = async () => {
  const refresh_token = localStorage.getItem('refresh_token');
  if (refresh_token) {
    try {
      await api.post('/accounts/logout/', { refresh: refresh_token });
    } catch (error) {
      console.error('Logout error:', error);
    }
  }
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
};

export default api; 