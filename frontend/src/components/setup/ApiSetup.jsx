import { useState } from 'react'
import { motion } from 'framer-motion'
import { CheckCircle, AlertCircle, Loader, ExternalLink, ChevronRight, Info } from 'lucide-react'
import api from '../../api/client'
import useProjectStore from '../../store/projectStore'

export default function ApiSetup({ onComplete }) {
  const [projectId, setProjectId] = useState('')
  const [status, setStatus]       = useState('idle')   // idle | loading | success | error
  const [message, setMessage]     = useState('')
  const { setApiKeys }            = useProjectStore()

  const handleSubmit = async () => {
    if (!projectId.trim()) {
      setStatus('error')
      setMessage('Project ID를 입력해주세요')
      return
    }

    setStatus('loading')
    setMessage('')

    try {
      const res = await api.post('/setup/validate', { project_id: projectId.trim() })
      if (res.data.success) {
        setStatus('success')
        setTimeout(() => {
          setApiKeys({ projectId: projectId.trim() })
          onComplete?.()
        }, 900)
      }
    } catch (e) {
      setStatus('error')
      setMessage(e.message || 'Vertex AI 연결 실패')
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') handleSubmit()
  }

  return (
    <div
      className="min-h-screen flex flex-col items-center justify-center p-4"
      style={{ background: 'radial-gradient(ellipse 80% 50% at 50% -10%, rgba(249,115,22,0.08), transparent), #2C1A0A' }}
    >
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="text-center mb-8">
        <div className="text-5xl mb-3">🚁</div>
        <h1 className="text-2xl font-bold tracking-widest text-stone-200">MV GENERATOR</h1>
        <p className="text-stone-500 text-sm mt-1">AI 뮤직비디오 메이커</p>
      </motion.div>

      {/* Main Card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
        className="w-full max-w-md bg-card border border-border rounded-2xl p-6 shadow-2xl space-y-5"
      >
        <div>
          <h2 className="text-lg font-semibold text-stone-200 flex items-center gap-2">
            🔑 Google Cloud 연결
            <span className="text-xs text-stone-500 font-normal">(처음 한 번만)</span>
          </h2>
          <p className="text-xs text-stone-500 mt-1">Vertex AI 서비스 계정으로 인증합니다</p>
        </div>

        {/* Project ID */}
        <div>
          <label className="block text-xs text-stone-500 mb-1.5">Google Cloud Project ID</label>
          <input
            type="text"
            value={projectId}
            onChange={(e) => setProjectId(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="my-project-123456"
            className="w-full bg-elevated border border-border rounded-xl px-3 py-2.5 text-sm text-stone-300 placeholder-stone-500 focus:outline-none focus:border-orange-500 transition-colors"
          />
          <a
            href="https://console.cloud.google.com"
            target="_blank" rel="noopener noreferrer"
            className="flex items-center gap-1 mt-1 text-xs text-orange-400 hover:text-orange-300 transition-colors"
          >
            <ExternalLink size={10} />
            console.cloud.google.com 에서 프로젝트 ID 확인
          </a>
        </div>

        {/* ADC 인증 안내 */}
        <div className="bg-elevated border border-border rounded-xl p-3 space-y-2">
          <div className="flex items-center gap-2 text-xs text-stone-400 font-medium">
            <Info size={14} className="text-orange-400" />
            인증 설정 — gcloud ADC (JSON 키 불필요)
          </div>
          <ol className="text-xs text-stone-500 space-y-1.5 list-decimal list-inside">
            <li>
              <a href="https://cloud.google.com/sdk/docs/install" target="_blank" rel="noopener noreferrer"
                className="text-orange-400 hover:text-orange-300">Google Cloud CLI 설치</a>
            </li>
            <li>터미널에서 실행:
              <div className="mt-1 ml-4 font-mono bg-primary rounded px-2 py-1 text-stone-300 select-all">
                gcloud auth application-default login
              </div>
            </li>
            <li>프로젝트 지정:
              <div className="mt-1 ml-4 font-mono bg-primary rounded px-2 py-1 text-stone-300 select-all">
                gcloud auth application-default set-quota-project {'{PROJECT_ID}'}
              </div>
            </li>
          </ol>
        </div>

        {/* Error */}
        {status === 'error' && (
          <div className="flex items-start gap-2 p-3 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400 text-xs">
            <AlertCircle size={14} className="shrink-0 mt-0.5" />
            <span>{message}</span>
          </div>
        )}

        {/* Submit */}
        <button
          onClick={handleSubmit}
          disabled={status === 'loading' || status === 'success'}
          className="w-full py-3 rounded-xl btn-primary text-white font-semibold text-sm flex items-center justify-center gap-2 disabled:opacity-60 disabled:cursor-not-allowed"
        >
          {status === 'loading' && <Loader size={15} className="animate-spin" />}
          {status === 'success' && <CheckCircle size={15} className="text-green-300" />}
          {status === 'idle'    && <ChevronRight size={15} />}
          {status === 'loading' ? 'Vertex AI 연결 확인 중...'
            : status === 'success' ? '연결 성공!'
            : '연결 확인 후 시작하기'}
        </button>
      </motion.div>

      {/* Bottom info */}
      <motion.div
        initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }}
        className="mt-6 text-center space-y-2"
      >
        <div className="flex flex-wrap justify-center gap-2">
          {['🎵 Lyria 3 Pro', '🖼️ Nano Banana 2', '🎬 Veo 3.1 Fast'].map((chip) => (
            <span key={chip} className="px-3 py-1 rounded-full bg-elevated border border-border text-xs text-stone-400">{chip}</span>
          ))}
        </div>
        <p className="text-xs text-stone-500">✦ $300 무료 크레딧으로 뮤직비디오 약 <span className="text-stone-300">23편</span></p>
        <p className="text-xs text-yellow-600/80">⚠️ 유료 업그레이드만 안 하면 청구되지 않습니다</p>
      </motion.div>
    </div>
  )
}
