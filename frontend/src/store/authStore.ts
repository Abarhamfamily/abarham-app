import { create } from 'zustand'
import type { User } from '../types'

interface AuthState {
  accessToken: string | null
  refreshToken: string | null
  user: User | null
  setAuth: (accessToken: string, refreshToken: string, user: User) => void
  clearAuth: () => void
}

const STORAGE_KEY = 'abarham-auth'

function loadInitial(): Pick<AuthState, 'accessToken' | 'refreshToken' | 'user'> {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return { accessToken: null, refreshToken: null, user: null }
    return JSON.parse(raw)
  } catch {
    return { accessToken: null, refreshToken: null, user: null }
  }
}

export const useAuthStore = create<AuthState>((set) => ({
  ...loadInitial(),
  setAuth: (accessToken, refreshToken, user) => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ accessToken, refreshToken, user }))
    set({ accessToken, refreshToken, user })
  },
  clearAuth: () => {
    localStorage.removeItem(STORAGE_KEY)
    set({ accessToken: null, refreshToken: null, user: null })
  },
}))
