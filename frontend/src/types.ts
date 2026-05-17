export interface DealClaim {
  type: string
  type_label: string
  description: string
  platform: string
  verified: boolean | null
}

export interface DealCardData {
  id: number | null
  product_name: string
  product_url: string
  original_price: number | null
  claimed_price: number | null
  verified_price: number | null
  claims: DealClaim[]
  steps: string[]
  valid_from: string | null
  valid_until: string | null
  status: string
  status_label: string
  status_icon: string
  source: string
  source_name: string
  created_at: string
}

export interface SubmitResponse {
  success: boolean
  card?: DealCardData
  error?: string
}

export interface ListResponse {
  deals: DealCardData[]
  total: number
}
