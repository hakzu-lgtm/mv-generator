import { useState, useCallback } from 'react'
import api from '../api/client'
import useProjectStore from '../store/projectStore'

const SAFE_LIMIT = 250

export function useCostGuard() {
  const { projectId, sessionCost, setSessionCost } = useProjectStore()
  const [checking, setChecking] = useState(false)
  const [breakdown, setBreakdown] = useState({})

  const checkCost = useCallback(async (service, qty) => {
    setChecking(true)
    try {
      const res = await api.post('/costs/check', { project_id: projectId, service, qty })
      return res.data
    } catch {
      return { estimated: 0, can_proceed: true, would_total: sessionCost }
    } finally {
      setChecking(false)
    }
  }, [projectId, sessionCost])

  const refreshCost = useCallback(async () => {
    try {
      const res = await api.get(`/costs/${projectId}`)
      setSessionCost(res.data.total)
      setBreakdown(res.data.breakdown || {})
      return res.data
    } catch {
      return { total: sessionCost, limit: SAFE_LIMIT }
    }
  }, [projectId, setSessionCost, sessionCost])

  const isOverLimit = sessionCost >= SAFE_LIMIT
  const remaining = Math.max(0, SAFE_LIMIT - sessionCost)
  const percentage = Math.min(100, (sessionCost / SAFE_LIMIT) * 100)

  return {
    sessionCost,
    breakdown,
    remaining,
    percentage,
    isOverLimit,
    checkCost,
    refreshCost,
    checking,
    limit: SAFE_LIMIT,
  }
}
