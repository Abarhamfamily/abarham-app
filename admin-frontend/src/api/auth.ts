import { adminApiClient } from './client'
import type { AdminTokenResponse, Admin } from '../types'

export async function adminLogin(username: string, password: string) {
  const { data } = await adminApiClient.post<AdminTokenResponse>('/auth/login', {
    username,
    password,
  })
  return data
}

export async function adminMe() {
  const { data } = await adminApiClient.get<Admin>('/auth/me')
  return data
}

export async function adminLogout() {
  await adminApiClient.post('/auth/logout')
}

export async function adminChangePassword(current_password: string, new_password: string) {
  await adminApiClient.post('/auth/change-password', { current_password, new_password })
}
