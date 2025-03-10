import axios, { AxiosError, AxiosRequestConfig, AxiosResponse } from 'axios';

// Determine the base URL based on environment
const getBaseUrl = () => {
  if (process.env.REACT_APP_API_URL) {
    return process.env.REACT_APP_API_URL;
  }
  
  if (process.env.NODE_ENV === 'production') {
    return '/api'; // In production, API is typically served from the same domain
  }
  
  return 'http://localhost:8000/api'; // Default development API URL
};

const api = axios.create({
  baseURL: getBaseUrl(),
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds timeout
});

// Request interceptor
api.interceptors.request.use((config) => {
  // Get token from localStorage
  const token = localStorage.getItem('token');
  
  // If token exists, add to headers
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  
  // Log API requests in development
  if (process.env.NODE_ENV === 'development') {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`, 
      config.params || config.data || '');
  }
  
  return config;
}, (error) => {
  return Promise.reject(error);
});

// Response interceptor
api.interceptors.response.use(
  (response: AxiosResponse) => {
    // Wrap successful responses in the expected format if they're not already
    if (!response.data.hasOwnProperty('data')) {
      return {
        ...response,
        data: {
          data: response.data,
          status: response.status,
          message: 'OK'
        }
      };
    }
    return response;
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean };
    
    // Handle unauthorized errors (expired token)
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // Attempt to refresh the token
        const refreshToken = localStorage.getItem('refreshToken');
        
        if (refreshToken) {
          const response = await axios.post(`${getBaseUrl()}/auth/refresh-token`, {
            refresh_token: refreshToken
          });
          
          if (response.data.access_token) {
            localStorage.setItem('token', response.data.access_token);
            
            // Update the authorization header
            api.defaults.headers.common['Authorization'] = `Bearer ${response.data.access_token}`;
            
            // Retry the original request
            if (originalRequest.headers) {
              originalRequest.headers['Authorization'] = `Bearer ${response.data.access_token}`;
            }
            return api(originalRequest);
          }
        }
      } catch (refreshError) {
        // If refresh token is invalid/expired, logout the user
        localStorage.removeItem('token');
        localStorage.removeItem('refreshToken');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    // If not a token error, or token refresh failed, reject with original error
    return Promise.reject(error);
  }
);

export default api;
