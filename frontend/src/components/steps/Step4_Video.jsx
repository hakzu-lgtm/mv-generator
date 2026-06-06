import { useState } from 'react'
import { motion } from 'framer-motion'
import { Film, ChevronRight, RefreshCw, CheckCircle, AlertTriangle, RotateCcw } from 'lucide-react'
import toast from 'react-hot-toast'
import api, { postSSE } from '../../api/client'
import useProjectStore from '../../store/projectStore'
import SceneGrid from '../ui/SceneGrid'
import CostGate from '../ui/CostGate'
import ProgressBar from '../ui/ProgressBar'
import { useCostGuard } from '../../hooks/useCostGuard'

export default function Step4_Video() {
  const { projectId, scenes, charBasePrompt, selectedStyle, clips, setClips, setStep, markStepComplete } = useProjectStore()
  const { sessionCost, isOverLimit, refreshCost } = useCostGuard()

  const [showGate, setShowGate] = useState(false)
  const [running, setRunning] = useState(false)
  const [logs, setLogs] = useState([])
  const [generatedClips, setGeneratedClips] = useState([])
  const [accumulatedCost, setAccumulatedCost] = useState(0)

  const handleResetCost = async () => {
    try {
      await api.delete(`/costs/${projectId}/reset`)
      await refreshCost()
      toast.success('세션 비용 초기화 완료')
    } catch (e) {
      toast.error(e.message)
    }
  }

  const sceneCount = scenes?.length || 10
  const secPerScene = 8
  const totalSeconds = sceneCount * secPerScene
  const estimatedCost = totalSeconds * 0.15
  const wouldTotal = sessionCost + estimatedCost

  const handleGenerate = async () => {
    setShowGate(false)
    setRunning(true)
    setLogs([])
    setAccumulatedCost(0)

    await postSSE(
      '/api/video/generate',
      {
        project_id: projectId,
        char_base_prompt: charBasePrompt,
        style: selectedStyle,
      },
      (data) => {
        setLogs((l) => [...l, { ...data, time: Date.now() }])
        if (data.accumulated !== undefined) setAccumulatedCost(data.accumulated)
      },
      (err) => { toast.error(err.message); setRunning(false) },
      async (data) => {
        const clips        = data.clips || []
        const safetyBlocked = clips.filter(c => c.safety_blocked).length
        setGeneratedClips(clips)
        setClips(clips)
        await refreshCost()
        if ((data.failed ?? 0) === 0) markStepComplete(5)
        if (safetyBlocked > 0) {
          toast(`영상 생성 완료. 안전 필터로 ${safetyBlocked}개 씬 차단됨 — 재생성에서 직접 묘사를 수정하세요.`, { duration: 6000 })
        } else {
          toast.success(data.summary || '영상 생성 완료!')
        }
        setRunning(false)
      }
    )
  }

  const handleConfirm = () => {
    markStepComplete(5)
    setStep(6)
    toast.success('영상 확정! 최종 편집으로 이동합니다')
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6 animate-fade-in">
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-2xl font-bold text-stone-200">영상 생성</h2>
          <p className="text-stone-500 text-sm mt-0.5">Veo 3.1 Fast로 각 씬을 영상으로 변환합니다</p>
        </div>
        <button onClick={handleResetCost}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-border text-stone-500 text-xs hover:text-stone-300 hover:border-stone-500 transition-all">
          <RotateCcw size={12} />세션 비용 초기화
        </button>
      </div>

      <CostGate
        isOpen={showGate}
        onConfirm={handleGenerate}
        onCancel={() => setShowGate(false)}
        estimated={estimatedCost}
        service={`Veo 3.1 Fast · ${sceneCount}씬 × ${secPerScene}초`}
        currentTotal={sessionCost}
      />

      {/* Cost preview card */}
      <div className={`bg-card border rounded-2xl p-5 ${wouldTotal > 200 ? 'border-yellow-500/40' : 'border-border'}`}>
        <div className="flex items-center gap-2 mb-3">
          <AlertTriangle size={16} className="text-yellow-500" />
          <h3 className="text-sm font-semibold text-stone-300">비용 예상 (가장 비싼 단계)</h3>
        </div>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-stone-400">{sceneCount}씬 × {secPerScene}초</span>
            <span className="text-stone-300 font-mono">{totalSeconds}초</span>
          </div>
          <div className="flex justify-between">
            <span className="text-stone-400">단가</span>
            <span className="text-stone-300 font-mono">$0.15/초</span>
          </div>
          <div className="border-t border-border pt-2 flex justify-between font-semibold">
            <span className="text-stone-300">이번 작업 예상</span>
            <span className="text-orange-400 font-mono">${estimatedCost.toFixed(2)}</span>
          </div>
          <div className="flex justify-between text-xs text-stone-500">
            <span>세션 누적: ${sessionCost.toFixed(2)} → ${wouldTotal.toFixed(2)}</span>
            <span>한도 $250</span>
          </div>
        </div>

        {running && (
          <div className="mt-3 pt-3 border-t border-border">
            <div className="flex justify-between text-xs text-stone-500 mb-1">
              <span>실시간 누적 비용</span>
              <span className="text-orange-400 font-mono font-semibold">${accumulatedCost.toFixed(2)}</span>
            </div>
          </div>
        )}
      </div>

      {isOverLimit ? (
        <div className="py-6 text-center">
          <AlertTriangle size={32} className="mx-auto mb-2 text-red-400" />
          <p className="text-red-400 text-sm">안전 한도 도달 — 영상 생성 불가</p>
        </div>
      ) : (
        <button
          onClick={() => !running && setShowGate(true)}
          disabled={running}
          className="w-full py-4 rounded-2xl btn-primary text-white font-semibold text-base flex items-center justify-center gap-2"
        >
          {running ? (
            <>
              <div className="flex gap-1">{[0,1,2,3,4].map(i => <span key={i} className="wave-bar h-5" style={{ animationDelay: `${i*0.15}s` }} />)}</div>
              영상 생성 중...
            </>
          ) : (
            <><Film size={18} />🎬 영상 생성 시작</>
          )}
        </button>
      )}

      {(running || logs.length > 0) && <ProgressBar logs={logs} running={running} />}

      {/* Scene clips */}
      {generatedClips.length > 0 && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-3">
          <h3 className="text-sm font-semibold text-stone-300">생성된 영상 씬</h3>
          <SceneGrid scenes={generatedClips} projectId={projectId} type="video" />

          <div className="flex gap-3 mt-4">
            <button onClick={() => setShowGate(true)} disabled={running || isOverLimit}
              className="flex-1 py-3 rounded-xl border border-border text-stone-400 hover:text-stone-300 flex items-center justify-center gap-2 text-sm transition-all">
              <RefreshCw size={14} />재생성
            </button>
            <button onClick={handleConfirm}
              className="flex-1 py-3 rounded-xl btn-primary text-white font-semibold text-sm flex items-center justify-center gap-2">
              <CheckCircle size={14} />확정 완료 — 최종편집으로<ChevronRight size={14} />
            </button>
          </div>
        </motion.div>
      )}
    </div>
  )
}
