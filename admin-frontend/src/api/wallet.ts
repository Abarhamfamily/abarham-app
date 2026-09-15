import { adminApiClient } from './client'
import type { AdminWallet, AdminTransaction, ListMeta, AdminWithdrawal } from '../types'

export async function fetchWallets(params: { search?: string; limit?: number; offset?: number }) {
  const { data } = await adminApiClient.get<{ data: AdminWallet[]; meta: ListMeta }>('/wallet', { params })
  return data
}

export async function fetchWalletTransactions(walletId: string, params?: { limit?: number; offset?: number }) {
  const { data } = await adminApiClient.get<AdminTransaction[]>(`/wallet/${walletId}/transactions`, { params })
  return data
}

export async function adjustWallet(walletId: string, amount: string, description: string) {
  const { data } = await adminApiClient.post<AdminTransaction>(`/wallet/${walletId}/adjust`, {
    amount,
    description,
  })
  return data
}

export async function fetchWithdrawals(params: { status?: string; limit?: number; offset?: number }) {
  const { data } = await adminApiClient.get<AdminWithdrawal[]>('/wallet/withdrawals', { params })
  return data
}

export async function approveWithdrawal(id: string) {
  const { data } = await adminApiClient.post<AdminTransaction>(`/wallet/withdrawals/${id}/approve`)
  return data
}

export async function rejectWithdrawal(id: string, reason?: string) {
  const { data } = await adminApiClient.post<AdminTransaction>(`/wallet/withdrawals/${id}/reject`, { reason })
  return data
}
