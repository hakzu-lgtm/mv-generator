import { useEffect } from 'react'
import useProjectStore from '../store/projectStore'

export function useApiKeys() {
  const { apiKeys, setApiKeys, clearApiKeys } = useProjectStore()

  const saveKeys = (keys) => {
    setApiKeys(keys)
  }

  const removeKeys = () => {
    clearApiKeys()
  }

  return { apiKeys, saveKeys, removeKeys, isReady: !!apiKeys }
}
