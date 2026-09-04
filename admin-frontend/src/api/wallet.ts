import { adminApiClient } from './client'
import type { AdminWallet, AdminTransaction, ListMeta } from '../types'

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
