import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance with interceptors
const api = axios.create({
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
        await axios.post(`${API_BASE_URL}/auth/refresh-cookie`, {}, {
          withCredentials: true
        });

        // Retry original request
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh token หมดอายุ - logout
        logout();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export const authService = {
  // ดึงข้อมูล user ปัจจุบัน
  getCurrentUser: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },

  // Login ด้วย Google
  loginWithGoogle: () => {
    window.location.href = `${API_BASE_URL}/auth/google/login`;
  },

  // Logout
  logout: async () => {
    try {
      await api.post('/auth/logout');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // ลบข้อมูล user ใน localStorage (ถ้ามี)
      localStorage.removeItem('user');
    }
  },

  // ตรวจสอบว่า login อยู่มั้ย (ต้องเรียก API)
  isAuthenticated: async () => {
    try {
      await api.get('/auth/me');
      return true;
    } catch (error) {
      return false;
    }
  },

  // ดึง user จาก localStorage (cache)
  getUser: () => {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  }
};

export const logout = () => {
  localStorage.removeItem('user');
};

export default api;
