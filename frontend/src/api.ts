import type { SubmitResponse, ListResponse } from './types'

const BASE = '/api'

export async function submitDeal(content: string, source = 'manual', sourceName = ''): Promise<SubmitResponse> {
  const res = await fetch(`${BASE}/deals/submit`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content, source, source_name: sourceName }),
  })
  return res.json()
}

export async function listDeals(status?: string): Promise<ListResponse> {
  const params = status ? `?status=${status}` : ''
  const res = await fetch(`${BASE}/deals${params}`)
  return res.json()
}
