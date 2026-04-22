import axios, { AxiosInstance, InternalAxiosRequestConfig, AxiosError } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

interface TokenData {
  access_token: string;
  refresh_token?: string;
  expires_in: number;
}

const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  // Seguridad: limitar payload
  maxBodyLength: 10 * 1024 * 1024, // 10MB
  maxContentLength: 10 * 1024 * 1024,
  // Timeouts
  timeout: 30000,
});

// ──────────────────── REQUEST INTERCEPTOR ────────────────────
api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = localStorage.getItem('access_token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  
  // Headers de seguridad adicionales
  if (config.headers) {
    config.headers['X-Requested-With'] = 'XMLHttpRequest';
  }
  
  return config;
});

// ──────────────────── RESPONSE INTERCEPTOR ────────────────────
api.interceptors.response.use(
  (response) => {
    // Renovar token si viene en la respuesta (refresh)
    if (response.data?.access_token) {
      localStorage.setItem('access_token', response.data.access_token);
      if (response.data.refresh_token) {
        localStorage.setItem('refresh_token', response.data.refresh_token);
      }
    }
    return response;
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    // Manejar token expirado
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      const refreshToken = localStorage.getItem('refresh_token');
      
      if (refreshToken) {
        try {
          // Intentar renovar token
          const refreshResponse = await axios.post<TokenData>(
            `${API_BASE_URL}/api/v1/auth/refresh`,
            {},
            {
              headers: {
                Authorization: `Bearer ${refreshToken}`,
              },
            }
          );

          const { access_token } = refreshResponse.data;
          localStorage.setItem('access_token', access_token);

          // Reintentar request original
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${access_token}`;
          }
          return api(originalRequest);
        } catch (refreshError) {
          // Refresh token expiró
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          localStorage.removeItem('user');
          window.location.href = '/login';
          return Promise.reject(refreshError);
        }
      } else {
        // Sin refresh token, ir a login
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        window.location.href = '/login';
      }
    }

    // Manejar errores de rate limit
    if (error.response?.status === 429) {
      const retryAfter = error.response?.headers['retry-after'] || '60';
      console.warn(`Rate limited. Retry after ${retryAfter} seconds`);
    }

    return Promise.reject(error);
  }
);

export default api;
