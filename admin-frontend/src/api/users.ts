import { adminApiClient } from './client'
import type { AdminUser, AdminUserDetail, ListMeta } from '../types'

export async function fetchUsers(params: { search?: string; is_active?: boolean; limit?: number; offset?: number }) {
  const { data } = await adminApiClient.get<{ data: AdminUser[]; meta: ListMeta }>('/users', { params })
  return data
}

export async function fetchUser(id: string) {
  const { data } = await adminApiClient.get<AdminUserDetail>(`/users/${id}`)
  return data
}

export async function updateUser(id: string, payload: Partial<Pick<AdminUser, 'full_name' | 'email' | 'is_active'>>) {
  const { data } = await adminApiClient.patch<AdminUser>(`/users/${id}`, payload)
  return data
}
