import { useEffect, useState } from 'react'
import ApiSetup from './components/setup/ApiSetup'
import MainApp from './components/layout/MainApp'
import Toast from './components/ui/Toast'
import useProjectStore from './store/projectStore'
import api from './api/client'

export default function App() {
  const { apiKeys, setApiKeys } = useProjectStore()
  const [validated, setValidated] = useState(false)
  const [validating, setValidating] = useState(false)

  useEffect(() => {
    if (apiKeys?.projectId && !validated) {
      setValidating(true)
      api.post('/setup/validate', { project_id: apiKeys.projectId })
        .then(() => setValidated(true))
        .catch(() => setApiKeys(null))
        .finally(() => setValidating(false))
    }
  }, [])

  if (validating) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-primary">
        <div className="text-center">
          <div className="text-4xl mb-3">🚁</div>
          <p className="text-slate-400 text-sm">Vertex AI 연결 확인 중...</p>
        </div>
      </div>
    )
  }

  if (!apiKeys?.projectId) {
    return (
      <>
        <ApiSetup onComplete={() => setValidated(true)} />
        <Toast />
      </>
    )
  }

  return (
    <>
      <MainApp />
      <Toast />
    </>
  )
}
