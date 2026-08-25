import { adminApiClient } from './client'
import type { AdminTrip, ListMeta } from '../types'

export interface TripFormValues {
  title: string
  destination: string
  description?: string
  start_date: string
  end_date: string
  price: string
  deposit_amount: string
  capacity: number
  status: string
  transportation_type?: string
  difficulty_level?: string
  accommodation_info?: string
  meeting_point?: string
  departure_time?: string
  cancellation_policy?: string
}

export async function fetchTrips(params: { status?: string; search?: string; limit?: number; offset?: number }) {
  const { data } = await adminApiClient.get<{ data: AdminTrip[]; meta: ListMeta }>('/trips', { params })
  return data
}

export async function fetchTrip(id: string) {
  const { data } = await adminApiClient.get<AdminTrip>(`/trips/${id}`)
  return data
}

export async function createTrip(payload: TripFormValues) {
  const { data } = await adminApiClient.post<AdminTrip>('/trips', payload)
  return data
}

export async function updateTrip(id: string, payload: Partial<TripFormValues>) {
  const { data } = await adminApiClient.put<AdminTrip>(`/trips/${id}`, payload)
  return data
}

export async function deleteTrip(id: string) {
  await adminApiClient.delete(`/trips/${id}`)
}
