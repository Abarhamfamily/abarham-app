import { describe, expect, it } from 'vitest'
import { fetchTrips } from './trips'

describe('fetchTrips', () => {
  it('returns paginated trip response with data and meta', async () => {
    const result = await fetchTrips()

    expect(result).toHaveProperty('data')
    expect(Array.isArray(result.data)).toBe(true)
    expect(result).toHaveProperty('meta')
    expect(result.meta).toHaveProperty('total')
  })
})
