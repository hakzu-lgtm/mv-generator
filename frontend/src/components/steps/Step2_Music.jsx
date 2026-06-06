import { useState } from 'react'
import { motion } from 'framer-motion'
import { Music, Upload, RefreshCw, ChevronRight, Loader } from 'lucide-react'
import { useDropzone } from 'react-dropzone'
import toast from 'react-hot-toast'
import api, { postSSE } from '../../api/client'
import useProjectStore from '../../store/projectStore'
import AudioPlayer from '../ui/AudioPlayer'
import CostGate from '../ui/CostGate'
import ProgressBar from '../ui/ProgressBar'
import { useCostGuard } from '../../hooks/useCostGuard'

export default function Step2_Music() {
  const { projectId, lyrics, setMusic, music, setStep, markStepComplete } = useProjectStore()
  const { sessionCost, isOverLimit, refreshCost } = useCostGuard()
  const [tab, setTab] = useState('ai')
  const [showGate, setShowGate] = useState(false)
  const [running, setRunning] = useState(false)
  const [logs, setLogs] = useState([])
  const [uploading, setUploading] = useState(false)

  const COST = 0.08

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: { 'audio/*': ['.mp3', '.wav', '.ogg', '.m4a'] },
    maxFiles: 1,
    onDrop: async (files) => {
      if (!files[0]) return
      setUploading(true)
      try {
        const form = new FormData()
        form.append('file', files[0])
        const res = await api.post(`/music/upload?project_id=${projectId}`, form, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
        setMusic(res.data.meta)
        markStepComplete(3)
        toast.success('파일 업로드 완료!')
      } catch (e) {
        toast.error(e.message)
      } finally {
        setUploading(false)
      }
    }
  })

  const startGenerate = async () => {
    if (isOverLimit) { toast.error('안전 한도 초과'); return }
    setShowGate(false)
    setRunning(true)
    setLogs([])

    await postSSE(
      '/api/music/generate',
      { project_id: projectId },
      (data) => setLogs((l) => [...l, { ...data, time: Date.now() }]),
      (err) => { toast.error(err.message); setRunning(false) },
      async (data) => {
        setMusic(data.meta)
        await refreshCost()
        markStepComplete(3)
        toast.success('음악 생성 완료!')
        setRunning(false)
      }
    )
  }

  const handleConfirm = () => {
    if (!music) { toast.error('음악을 먼저 생성하거나 업로드해주세요'); return }
    markStepComplete(3)
    setStep(4)
    toast.success('음악 확정! 이미지 생성으로 이동합니다')
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6 animate-fade-in">
      <div>
        <h2 className="text-2xl font-bold text-stone-200">음악 생성</h2>
        <p className="text-stone-500 text-sm mt-0.5">Lyria 3 Pro로 AI 작곡하거나 파일을 업로드하세요</p>
      </div>

      <CostGate
        isOpen={showGate}
        onConfirm={startGenerate}
        onCancel={() => setShowGate(false)}
        estimated={COST}
        service="Lyria 3 Pro 음악 생성"
        currentTotal={sessionCost}
      />

      {/* Tabs */}
      <div className="flex bg-elevated rounded-xl p-1 border border-border">
        {[['ai', '🤖 AI 작곡', `$${COST}`], ['upload', '📁 파일 업로드', '무료']].map(([key, label, cost]) => (
          <button key={key} onClick={() => setTab(key)}
            className={`flex-1 py-2 rounded-lg text-sm font-medium transition-all flex items-center justify-center gap-2 ${tab === key ? 'bg-card text-stone-200 shadow' : 'text-stone-500 hover:text-stone-300'}`}>
            {label}
            <span className={`text-xs px-1.5 py-0.5 rounded-full ${key === 'ai' ? 'bg-orange-500/20 text-orange-400' : 'bg-green-500/20 text-green-400'}`}>{cost}</span>
          </button>
        ))}
      </div>

      {tab === 'ai' ? (
        <div className="space-y-4">
          {/* Summary */}
          {lyrics && (
            <div className="bg-card border border-border rounded-xl p-4">
              <h4 className="text-xs text-stone-500 mb-2">설정 요약</h4>
              <div className="flex gap-4 text-sm text-stone-300">
                <span>장르: {lyrics.genre?.join(', ')}</span>
                <span>BPM: {lyrics.music?.bpm}</span>
                <span>보컬: {lyrics.vocalist?.gender} {lyrics.vocalist?.style}</span>
              </div>
              {lyrics.lyria_prompt && (
                <details className="mt-2">
                  <summary className="text-xs text-stone-500 cursor-pointer hover:text-stone-400">Lyria 프롬프트 보기</summary>
                  <p className="mt-1 text-xs text-stone-500 bg-elevated rounded-lg p-2">{lyrics.lyria_prompt}</p>
                </details>
              )}
            </div>
          )}

          {/* Cost info */}
          <div className="flex items-center justify-between bg-stone-700/30 border border-stone-600/40 rounded-xl px-4 py-3">
            <span className="text-sm text-stone-300">Lyria 3 Pro · 1곡 생성</span>
            <span className="text-amber-400 font-mono font-semibold">${COST}</span>
          </div>

          {isOverLimit ? (
            <div className="py-4 text-center text-red-400 text-sm">안전 한도 도달 — 생성 불가</div>
          ) : (
            <button
              onClick={() => !running && setShowGate(true)}
              disabled={running}
              className="w-full py-4 rounded-2xl btn-primary text-white font-semibold text-base flex items-center justify-center gap-2"
            >
              {running ? (
                <>
                  <div className="flex gap-1">{[0,1,2,3,4].map(i => <span key={i} className="wave-bar h-5" style={{ animationDelay: `${i*0.15}s` }} />)}</div>
                  작곡 중...
                </>
              ) : (
                <><Music size={18} />🎵 작곡 시작</>
              )}
            </button>
          )}

          {(running || logs.length > 0) && <ProgressBar logs={logs} running={running} />}
        </div>
      ) : (
        <div>
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all ${isDragActive ? 'border-orange-500 bg-orange-500/5' : 'border-border hover:border-stone-500'}`}
          >
            <input {...getInputProps()} />
            <Upload size={32} className="mx-auto mb-3 text-stone-500" />
            <p className="text-stone-400 text-sm">{isDragActive ? '드롭하세요!' : 'MP3, WAV, OGG 파일을 드롭하거나 클릭해서 업로드'}</p>
            <p className="text-stone-500 text-xs mt-1">최대 50MB · 비용 없음</p>
          </div>
          {uploading && <p className="text-center text-orange-400 text-sm mt-3 flex items-center justify-center gap-2"><Loader size={14} className="animate-spin" />업로드 중...</p>}
        </div>
      )}

      {/* Music Player */}
      {music && (
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
          <AudioPlayer
            src={`/api/music/file/${projectId}`}
            title="생성된 음악"
            duration={music.duration}
            bpm={music.bpm}
          />
          <div className="flex gap-3 mt-3">
            <button onClick={() => setShowGate(true)} disabled={running || isOverLimit}
              className="flex-1 py-3 rounded-xl border border-border text-stone-400 hover:text-stone-300 flex items-center justify-center gap-2 text-sm transition-all">
              <RefreshCw size={14} />재생성
            </button>
            <button onClick={handleConfirm}
              className="flex-1 py-3 rounded-xl btn-primary text-white font-semibold text-sm flex items-center justify-center gap-2">
              이 음악으로 →<ChevronRight size={16} />
            </button>
          </div>
        </motion.div>
      )}
    </div>
  )
}
