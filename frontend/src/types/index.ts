export interface User {
  id: string
  phone_number: string
  full_name: string
  email?: string | null
  national_id?: string | null
  is_active: boolean
}

export interface Trip {
  id: string
  title: string
  destination: string
  description?: string | null
  start_date: string
  end_date: string
  price: string
  deposit_amount: string
  capacity: number
  remaining_capacity: number
  status: string
  transportation_type?: string | null
  difficulty_level?: string | null
  meeting_point?: string | null
  departure_time?: string | null
}

export interface TripListResponse {
  data: Trip[]
  meta: { total: number; limit: number; offset: number }
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  user: User
}
