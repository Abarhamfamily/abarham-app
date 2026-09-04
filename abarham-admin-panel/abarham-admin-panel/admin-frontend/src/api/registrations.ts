import { adminApiClient } from './client'
import type { AdminRegistration, ListMeta } from '../types'

export async function fetchRegistrations(params: {
  status?: string
  trip_id?: string
  user_id?: string
  limit?: number
  offset?: number
}) {
  const { data } = await adminApiClient.get<{ data: AdminRegistration[]; meta: ListMeta }>('/registrations', {
    params,
  })
  return data
}

export async function fetchRegistration(id: string) {
  const { data } = await adminApiClient.get<AdminRegistration>(`/registrations/${id}`)
  return data
}

export async function updateRegistrationStatus(id: string, status: string, notes?: string) {
  const { data } = await adminApiClient.patch<AdminRegistration>(`/registrations/${id}`, { status, notes })
  return data
}
