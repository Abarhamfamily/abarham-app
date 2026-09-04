import { create } from 'zustand'
import type { Admin } from '../types'

interface AdminAuthState {
  accessToken: string | null
  refreshToken: string | null
  admin: Admin | null
  setAuth: (accessToken: string, refreshToken: string, admin: Admin) => void
  setAccessToken: (accessToken: string) => void
  clearAuth: () => void
}

// نکته: کلید ذخیره‌سازی و کل namespace این store عمداً کاملاً جدا از
// User App است ('abarham-admin-auth' در برابر 'abarham-auth' در فرانت‌اند
// کاربری) تا هیچ overlap ای در localStorage یا state مرورگر رخ ندهد، حتی
// اگر هر دو اپ روی یک دامنه سرو شوند.
const STORAGE_KEY = 'abarham-admin-auth'

function loadInitial(): Pick<AdminAuthState, 'accessToken' | 'refreshToken' | 'admin'> {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return { accessToken: null, refreshToken: null, admin: null }
    return JSON.parse(raw)
  } catch {
    return { accessToken: null, refreshToken: null, admin: null }
  }
}

export const useAdminAuthStore = create<AdminAuthState>((set, get) => ({
  ...loadInitial(),
  setAuth: (accessToken, refreshToken, admin) => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ accessToken, refreshToken, admin }))
    set({ accessToken, refreshToken, admin })
  },
  setAccessToken: (accessToken) => {
    const { refreshToken, admin } = get()
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ accessToken, refreshToken, admin }))
    set({ accessToken })
  },
  clearAuth: () => {
    localStorage.removeItem(STORAGE_KEY)
    set({ accessToken: null, refreshToken: null, admin: null })
  },
}))
