import axios from 'axios'
import { useAuthStore } from '../store/authStore'

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
})

apiClient.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// TODO (Phase 2+): افزودن interceptor پاسخ برای refresh خودکار توکن هنگام 401
