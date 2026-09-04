import { apiClient } from './client'
import type { TokenResponse } from '../types'

export async function login(phone_number: string, password: string) {
  const { data } = await apiClient.post<TokenResponse>('/auth/login', { phone_number, password })
  return data
}

export async function register(phone_number: string, full_name: string, password: string) {
  const { data } = await apiClient.post<{ user_id: string; message: string }>('/auth/register', {
    phone_number,
    full_name,
    password,
  })
  return data
}
