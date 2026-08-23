import { apiClient } from './client'
import type { Trip, TripListResponse } from '../types'

export async function fetchTrips(params?: { status?: string; limit?: number; offset?: number }) {
  const { data } = await apiClient.get<TripListResponse>('/trips', { params })
  return data
}

export async function fetchTrip(id: string) {
  const { data } = await apiClient.get<Trip>(`/trips/${id}`)
  return data
}

export async function fetchTripAvailability(id: string) {
  const { data } = await apiClient.get(`/trips/${id}/availability`)
  return data
}
