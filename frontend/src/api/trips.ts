// frontend/src/api/trips.ts

import type { Trip, TripListResponse } from '../types'
import { mockTrips } from '../mocks/trips'

// 📦 دریافت تمام تورها (از Mock Data)
export function getMockTrips(): Trip[] {
  return [...mockTrips]
}

// 🌐 دریافت تورها (API یا Mock)
export async function fetchTrips(options?: { status?: string; limit?: number; offset?: number }): Promise<TripListResponse> {
  console.log('📡 Using mock trip list data')

  const pageSize = options?.limit ?? mockTrips.length
  const offset = options?.offset ?? 0
  const data = mockTrips.slice(offset, offset + pageSize)

  return {
    data,
    meta: {
      total: mockTrips.length,
      limit: pageSize,
      offset,
    },
  }
}

// 🔍 دریافت یک تور با ID (نام قدیمی)
export async function fetchTripById(id: string): Promise<Trip> {
  console.log(`📡 Using mock data for trip: ${id}`)
  const trips = getMockTrips()
  const trip = trips.find(t => t.id === id)
  if (!trip) {
    throw new Error('تور مورد نظر یافت نشد')
  }
  return trip
}

// 🔍 دریافت یک تور با ID (نام جدید - برای سازگاری با TripDetailsPage)
export async function fetchTrip(id: string): Promise<Trip> {
  return fetchTripById(id)
}

// 🪝 Hook سفارشی برای استفاده در کامپوننت‌ها
export function useTrips() {
  const trips = getMockTrips()
  return {
    trips,
    loading: false,
    error: null,
  }
}