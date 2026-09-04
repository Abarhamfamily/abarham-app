// frontend/src/mocks/trips.ts

import type { Trip, TripListResponse } from '../types'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

// Mock trip data for testing when API is unavailable
export const mockTrips: Trip[] = [
  {
    id: 'trip-001',
    title: 'ماجراجویی در دره چاکرود',
    description: 'سفر سه‌روزه به دره چاکرود با پیمایش در آب و کمپ در طبیعت بکر',
    images: [
      'https://images.unsplash.com/photo-1551632811-561732d1e306?w=800&h=400&fit=crop',
      'https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=800&h=400&fit=crop',
    ],
    price: '۲,۸۰۰,۰۰۰',
    deposit_amount: '۱,۰۰۰,۰۰۰',
    capacity: 12,
    remaining_capacity: 4,
    status: 'available',
    transportation_type: 'مینی بوس',
    difficulty_level: 'متوسط',
    meeting_point: 'میدان آزادی، تهران',
    departure_time: '۰۶:۰۰',
    destination: 'چاکرود، مازندران',
    start_date: '2025-05-15',
    end_date: '2025-05-18',
  },
  {
    id: 'trip-002',
    title: 'کمپینگ و طبیعت‌گردی در جنگل‌های مازندران',
    description: 'یک سفر دو روزه به دل جنگل‌های بکر مازندران با امکانات کامل کمپ',
    images: [
      'https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=800&h=400&fit=crop',
      'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=800&h=400&fit=crop',
    ],
    price: '۱,۸۰۰,۰۰۰',
    deposit_amount: '۵۰۰,۰۰۰',
    capacity: 15,
    remaining_capacity: 8,
    status: 'available',
    transportation_type: 'ون',
    difficulty_level: 'آسان',
    meeting_point: 'میدان ونک، تهران',
    departure_time: '۰۷:۰۰',
    destination: 'جنگل‌های گرمسیری مازندران',
    start_date: '2025-05-20',
    end_date: '2025-05-22',
  },
  {
    id: 'trip-003',
    title: 'دوچرخه‌سواری در مسیرهای ساحلی بلوچستان',
    description: 'چهار روز دوچرخه‌سواری در مسیرهای ساحلی بلوچستان با مناظر بکر',
    images: [
      'https://images.unsplash.com/photo-1571068316344-75bc76f77890?w=800&h=400&fit=crop',
      'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&h=400&fit=crop',
    ],
    price: '۳,۰۰۰,۰۰۰',
    deposit_amount: '۱,۰۰۰,۰۰۰',
    capacity: 8,
    remaining_capacity: 2,
    status: 'available',
    transportation_type: 'وانت',
    difficulty_level: 'سخت',
    meeting_point: 'میدان آزادی، تهران',
    departure_time: '۰۵:۰۰',
    destination: 'ساحل بلوچستان',
    start_date: '2025-06-01',
    end_date: '2025-06-05',
  },
]

export async function fetchTrips(): Promise<TripListResponse> {
  try {
    const response = await axios.get(`${API_BASE_URL}/trips`)
    return {
      data: response.data.data ?? [],
      meta: response.data.meta ?? {
        total: response.data.data?.length ?? 0,
        limit: response.data.data?.length ?? 0,
        offset: 0,
      },
    }
  } catch (error) {
    console.warn('API unavailable, using mock data:', error)

    return {
      data: mockTrips,
      meta: {
        total: mockTrips.length,
        limit: mockTrips.length,
        offset: 0,
      },
    }
  }
}

export async function fetchTripById(id: string): Promise<Trip> {
  try {
    const response = await axios.get(`${API_BASE_URL}/trips/${id}`)
    return response.data.data
  } catch (error) {
    console.warn('API unavailable, using mock data for trip:', error)
    const trip = mockTrips.find(t => t.id === id)
    if (!trip) {
      throw new Error('Trip not found')
    }
    return trip
  }
}