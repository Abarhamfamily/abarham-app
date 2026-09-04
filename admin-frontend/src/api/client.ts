import axios from 'axios'
import { useAdminAuthStore } from '../store/adminAuthStore'

// baseURL به /api/v1/admin ختم می‌شود؛ این کلاینت هرگز به endpoint های
// User App (/api/v1/auth, /api/v1/trips و ...) درخواست نمی‌زند.
export const adminApiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1/admin',
})

adminApiClient.interceptors.request.use((config) => {
  const token = useAdminAuthStore.getState().accessToken
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

let refreshPromise: Promise<string | null> | null = null

async function refreshAccessToken(): Promise<string | null> {
  const { refreshToken, setAccessToken, clearAuth } = useAdminAuthStore.getState()
  if (!refreshToken) return null

  try {
    const { data } = await axios.post(
      `${adminApiClient.defaults.baseURL}/auth/refresh`,
      { refresh_token: refreshToken }
    )
    setAccessToken(data.access_token)
    return data.access_token as string
  } catch {
    clearAuth()
    return null
  }
}

adminApiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    if (error.response?.status === 401 && !originalRequest._retry && originalRequest.url !== '/auth/login') {
      originalRequest._retry = true

      if (!refreshPromise) {
        refreshPromise = refreshAccessToken().finally(() => {
          refreshPromise = null
        })
      }

      const newToken = await refreshPromise
      if (newToken) {
        originalRequest.headers.Authorization = `Bearer ${newToken}`
        return adminApiClient(originalRequest)
      }
    }
    return Promise.reject(error)
  }
)
