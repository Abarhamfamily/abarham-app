import { adminApiClient } from './client'
import type { AdminPayment, ListMeta } from '../types'

export async function fetchPayments(params: { status?: string; limit?: number; offset?: number }) {
  const { data } = await adminApiClient.get<{ data: AdminPayment[]; meta: ListMeta }>('/payments', { params })
  return data
}

export async function fetchPayment(id: string) {
  const { data } = await adminApiClient.get<AdminPayment>(`/payments/${id}`)
  return data
}

export async function confirmPayment(id: string, reference_code?: string) {
  const { data } = await adminApiClient.post<AdminPayment>(`/payments/${id}/confirm`, { reference_code })
  return data
}

export async function rejectPayment(id: string, reason?: string) {
  const { data } = await adminApiClient.post<AdminPayment>(`/payments/${id}/reject`, { reason })
  return data
}
