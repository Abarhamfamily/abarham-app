import { adminApiClient } from './client'
import type { AdminNotification, ListMeta } from '../types'

export async function fetchNotifications(params: { user_id?: string; limit?: number; offset?: number }) {
  const { data } = await adminApiClient.get<{ data: AdminNotification[]; meta: ListMeta }>('/notifications', {
    params,
  })
  return data
}

export async function createNotification(payload: {
  title: string
  content: string
  type?: string
  user_id?: string
  all_active_users?: boolean
}) {
  const { data } = await adminApiClient.post<{ created_count: number }>('/notifications', payload)
  return data
}
