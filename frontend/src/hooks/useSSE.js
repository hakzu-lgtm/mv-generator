import { useState, useCallback, useRef } from 'react'
import { postSSE } from '../api/client'
import useProjectStore from '../store/projectStore'

export function useSSE() {
  const [running, setRunning] = useState(false)
  const [progress, setProgress] = useState([])
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const { addSseLog } = useProjectStore()
  const abortRef = useRef(false)

  const run = useCallback(async (url, body) => {
    setRunning(true)
    setProgress([])
    setResult(null)
    setError(null)
    abortRef.current = false

    await postSSE(
      url,
      body,
      (data) => {
        const msg = data.message || JSON.stringify(data)
        setProgress((p) => [...p, { ...data, time: Date.now() }])
        addSseLog(msg)
      },
      (err) => {
        setError(err.message)
        setRunning(false)
      },
      (data) => {
        setResult(data)
        setRunning(false)
      }
    )
  }, [addSseLog])

  const reset = useCallback(() => {
    setRunning(false)
    setProgress([])
    setResult(null)
    setError(null)
  }, [])

  return { running, progress, result, error, run, reset }
}
