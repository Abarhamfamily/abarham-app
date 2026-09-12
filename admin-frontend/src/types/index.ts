export interface Admin {
  id: string
  username: string
  full_name: string
  role: string
  is_active: boolean
}

export interface AdminTokenResponse {
  access_token: string
  refresh_token: string
  admin: Admin
}

export interface DashboardStats {
  total_users: number
  active_users: number
  total_trips: number
  published_trips: number
  total_registrations: number
  pending_payment_registrations: number
  confirmed_registrations: number
  pending_payments_count: number
  confirmed_payments_total: string
  total_wallet_balance: string
  unread_notifications: number
}

export interface AdminUser {
  id: string
  phone_number: string
  full_name: string
  email?: string | null
  national_id?: string | null
  is_active: boolean
  created_at: string
}

export interface AdminUserProfile {
  birth_date?: string | null
  emergency_contact_name?: string | null
  emergency_contact_phone?: string | null
  medical_notes?: string | null
  vehicle_has_capacity: boolean
  empty_seats: number
  profile_image_url?: string | null
  national_id_image_url?: string | null
}

export interface AdminUserDetail extends AdminUser {
  profile?: AdminUserProfile | null
}

export interface ListMeta {
  total: number
  limit: number
  offset: number
}

export interface AdminTrip {
  id: string
  title: string
  destination: string
  description?: string | null
  start_date: string
  end_date: string
  price: string
   other_vehicle_price?: string | null,
  deposit_amount: string
  capacity: number
  remaining_capacity: number
  version: number
  status: string
  transportation_type?: string | null
  difficulty_level?: string | null
  accommodation_info?: string | null
  meeting_point?: string | null
  departure_time?: string | null
  cancellation_policy?: string | null
  created_at: string
  updated_at: string
}

export interface AdminRegistration {
  id: string
  user_id: string
  trip_id: string
  status: string
  total_price: string
  deposit_paid: string
  remaining_amount: string
  passenger_count: number
  vehicle_type?: string | null
  empty_seats_provided: number
  notes?: string | null
  payment_deadline?: string | null
  registered_at: string
  confirmed_at?: string | null
  cancelled_at?: string | null
  user_full_name?: string | null
  user_phone_number?: string | null
  trip_title?: string | null
}

export interface AdminPayment {
  id: string
  registration_id: string
  user_id: string
  amount: string
  type: string
  status: string
  method?: string | null
  reference_code?: string | null
  receipt_url?: string | null
  description?: string | null
  confirmed_at?: string | null
  created_at: string
  user_full_name?: string | null
  user_phone_number?: string | null
  trip_title?: string | null
}

export interface AdminWallet {
  id: string
  user_id: string
  balance: string
  pending_balance: string
  total_deposited: string
  total_withdrawn: string
  user_full_name?: string | null
  user_phone_number?: string | null
}

export interface AdminTransaction {
  id: string
  wallet_id: string
  amount: string
  type: string
  status: string
  reference_id?: string | null
  description?: string | null
  created_at: string
}

export interface AdminNotification {
  id: string
  user_id: string
  type: string
  title: string
  content: string
  data?: Record<string, unknown> | null
  read_at?: string | null
  sent_at: string
  user_full_name?: string | null
}
