import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance with interceptors
export const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true, // สำคัญ! ต้องมีเพื่อส่ง cookies
});

// Response interceptor - จัดการ token หมดอายุ
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // เรียก refresh endpoint - cookies จะถูกส่งอัตโนมัติ
        await axios.post(`${API_BASE_URL}/refresh`, {}, {
          withCredentials: true
        });

        // Retry original request
        return api(originalRequest);
      } catch (refreshError) {
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error);
  }
);

export const authService = {
  // ดึงข้อมูล user ปัจจุบัน
  getCurrentUser: async () => {
    const response = await api.get('/me');
    return response.data;
  },

  // Login ด้วย Google
  loginWithGoogle: () => {
    window.location.href = `${API_BASE_URL}/auth/google/login`;
  },

  // Logout
  logout: async () => {
    try {
      await api.post('/logout');
    } catch (error) {
      console.error('Logout error:', error);
    }
  },

  // ตรวจสอบว่า login อยู่มั้ย (ต้องเรียก API)
  isAuthenticated: async () => {
    try {
      await api.get('/me');
      return true;
    } catch {
      return false;
    }
  }
}
export default api
