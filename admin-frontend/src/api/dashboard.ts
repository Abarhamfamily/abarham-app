import { adminApiClient } from './client'
import type { DashboardStats } from '../types'

export async function fetchDashboardStats() {
  const { data } = await adminApiClient.get<DashboardStats>('/dashboard')
  return data
}
