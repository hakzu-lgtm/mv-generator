import { useState } from 'react'
import { motion } from 'framer-motion'
import { Image, Zap, Hand, ChevronRight, Copy, ExternalLink, RefreshCw, User, CheckCircle, Loader } from 'lucide-react'
import { useDropzone } from 'react-dropzone'
import toast from 'react-hot-toast'
import api, { postSSE } from '../../api/client'
import useProjectStore from '../../store/projectStore'
import StyleCard from '../ui/StyleCard'
import SceneGrid from '../ui/SceneGrid'
import CostGate from '../ui/CostGate'
import ProgressBar from '../ui/ProgressBar'
import CharacterModal from '../ui/CharacterModal'
import { useCostGuard } from '../../hooks/useCostGuard'

const STYLES = ['한국웹툰시트', '시네마틱판타지', '지브리', '픽사3D', '클레이', '2D일러스트', '수채화', '일본애니', '시네마틱실사', '빈티지필름', '네온사이버펑크', '판타지', '미니멀모노톤', '마블코믹스', '오일페인팅', '픽셀아트', '수묵화']

export default function Step3_Images() {
  const { projectId, lyrics, selectedStyle, setSelectedStyle, character, setCharacter, charBasePrompt, setCharBasePrompt, scenes, setScenes, setStep, markStepComplete } = useProjectStore()
  const { sessionCost, isOverLimit, refreshCost } = useCostGuard()

  const [phase, setPhase] = useState('style') // style | character | generate
  const [showCharModal, setShowCharModal] = useState(false)
  const [showGate, setShowGate] = useState(false)
  const [gateConfig, setGateConfig] = useState({ service: '', cost: 0, action: null })
  const [generationMode, setGenerationMode] = useState('auto') // auto | manual
  const [running, setRunning] = useState(false)
  const [logs, setLogs] = useState([])
  const [generatedScenes, setGeneratedScenes] = useState([])
  const [charSheetDone, setCharSheetDone] = useState(false)
  const [charViews, setCharViews] = useState([])
  const [genSummary, setGenSummary] = useState(null) // {success, failed}
  const [retryRunning, setRetryRunning] = useState(false)

  const openGate = (service, cost, action) => {
    if (isOverLimit) { toast.error('안전 한도 초과'); return }
    setGateConfig({ service, cost, action })
    setShowGate(true)
  }

  const [preparing, setPreparing] = useState(false)

  const handlePrepareScenes = async (style) => {
    setPreparing(true)
    try {
      const res = await api.post('/images/prepare', { project_id: projectId, style })
      setScenes(res.data.scenes)
      toast.success(`${res.data.scenes.length}개 씬 준비 완료!`)
      setPhase('character')
    } catch (e) {
      toast.error(`씬 분할 실패: ${e.message}`)
    } finally {
      setPreparing(false)
    }
  }

  const handleStyleConfirm = async () => {
    await handlePrepareScenes(selectedStyle)
  }

  const handleCharacterConfirm = async (charData) => {
    setCharacter(charData)
    const base = `${charData.age} ${charData.gender}, ${charData.hair}, ${charData.outfit}${charData.feature ? ', ' + charData.feature : ''}, ${charData.mood}`
    setCharBasePrompt(base)
    toast.success('캐릭터 설정 완료')
  }

  const [charSheetLoading, setCharSheetLoading] = useState(false)
  const [assetError, setAssetError] = useState(null) // {error, error_type, trace}
  const [assetLogs, setAssetLogs] = useState([])

  const handleCharSheet = () => {
    openGate(
      '에셋 시트 생성 (주인공/조연/배경)',
      0.134 * 3,
      async () => {
        setCharSheetLoading(true)
        setAssetError(null)
        setAssetLogs([])
        setCharViews([])
        await postSSE(
          '/api/images/asset-sheets',
          { project_id: projectId, style: selectedStyle },
          (data) => {
            if (data.type === 'progress') {
              setAssetLogs(l => [...l, data.message])
            } else if (data.type === 'sheet_done') {
              const s = data.sheet
              setCharViews(prev => [...prev, { view: s.type, label: s.label, file: s.file, model: s.model, error: s.error }])
            }
          },
          (err, errData) => {
            setAssetError({ error: err.message, error_type: errData?.error_type || 'HTTPError', trace: errData?.trace || '' })
            toast.error(`에셋 시트 에러: ${err.message}`, { duration: 8000 })
            console.error('[asset-sheets error]', err)
            setCharSheetLoading(false)
          },
          async (data) => {
            const sheets = data.sheets || []
            setCharViews(sheets.map(s => ({ view: s.type, label: s.label, file: s.file, model: s.model, error: s.error })))
            setCharSheetDone(true)
            await refreshCost()
            const failed = sheets.filter(s => s.model === 'placeholder')
            if (failed.length > 0) {
              toast(`에셋 시트 부분 완료 (${failed.length}개 플레이스홀더)\n에러: ${data.errors?.join(' | ')?.slice(0, 120)}`, { duration: 6000 })
            } else {
              toast.success('에셋 시트 생성 완료!')
            }
            setCharSheetLoading(false)
          }
        )
      }
    )
  }

  const handleAutoGenerate = () => {
    const totalCost = (scenes?.length || 10) * 0.134  // Nano Banana Pro 최대 단가 기준
    openGate(
      `이미지 자동 생성 (${scenes?.length || '?'}장)`,
      totalCost,
      async () => {
        setRunning(true)
        setLogs([])
        setPhase('generate')
        await postSSE(
          '/api/images/generate-auto',
          { project_id: projectId, style: selectedStyle, char_base_prompt: charBasePrompt },
          (data) => setLogs((l) => [...l, { ...data, time: Date.now() }]),
          (err) => { toast.error(err.message); setRunning(false) },
          async (data) => {
            const results = data.results || []
            setGeneratedScenes(results)
            setGenSummary({ success: data.success ?? results.filter(r => r.model !== 'placeholder').length, failed: data.failed ?? results.filter(r => r.model === 'placeholder').length })
            await refreshCost()
            if ((data.failed ?? 0) === 0) markStepComplete(4)
            toast.success(data.summary || '이미지 생성 완료!')
            setRunning(false)
          }
        )
      }
    )
  }

  const handleRetryFailed = () => {
    const failedIds = generatedScenes.filter(s => s.failed || s.model === 'placeholder').map(s => s.scene_id)
    if (!failedIds.length) { toast('실패한 씬이 없습니다'); return }
    openGate(
      `실패 씬 ${failedIds.length}개 재생성`,
      failedIds.length * 0.134,
      async () => {
        setRetryRunning(true)
        setLogs([])
        await postSSE(
          '/api/images/regenerate-failed',
          { project_id: projectId, style: selectedStyle, char_base_prompt: charBasePrompt, failed_scene_ids: failedIds },
          (data) => setLogs((l) => [...l, { ...data, time: Date.now() }]),
          (err) => { toast.error(err.message); setRetryRunning(false) },
          async (data) => {
            // 재생성 결과를 기존 씬 목록에 병합
            const updates = Object.fromEntries((data.results || []).map(r => [r.scene_id, r]))
            setGeneratedScenes(prev => prev.map(s => updates[s.scene_id] ? { ...s, ...updates[s.scene_id] } : s))
            setGenSummary({ success: data.success, failed: data.failed })
            await refreshCost()
            if (data.failed === 0) markStepComplete(4)
            toast.success(data.summary || '재생성 완료!')
            setRetryRunning(false)
          }
        )
      }
    )
  }

  const handleConfirm = () => {
    markStepComplete(4)
    setStep(5)
    toast.success('이미지 확정! 영상 생성으로 이동합니다')
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6 animate-fade-in">
      <div>
        <h2 className="text-2xl font-bold text-stone-200">이미지 생성</h2>
        <p className="text-stone-500 text-sm mt-0.5">스타일 선택 → 캐릭터 설정 → 이미지 생성</p>
      </div>

      <CostGate
        isOpen={showGate}
        onConfirm={() => { setShowGate(false); gateConfig.action?.() }}
        onCancel={() => setShowGate(false)}
        estimated={gateConfig.cost}
        service={gateConfig.service}
        currentTotal={sessionCost}
      />

      <CharacterModal
        isOpen={showCharModal}
        onClose={() => setShowCharModal(false)}
        onConfirm={handleCharacterConfirm}
        initialData={character || {}}
      />

      {/* Phase indicator */}
      <div className="flex items-center gap-2 text-xs">
        {['스타일', '캐릭터', '이미지'].map((p, i) => {
          const phases = ['style', 'character', 'generate']
          const isCurrent = phase === phases[i]
          const isDone = phases.indexOf(phase) > i
          return (
            <div key={p} className="flex items-center gap-2">
              <span className={`flex items-center gap-1 px-2.5 py-1 rounded-full ${isDone ? 'text-green-400' : isCurrent ? 'text-orange-400 bg-orange-500/10' : 'text-stone-500'}`}>
                {isDone && <CheckCircle size={12} />}{p}
              </span>
              {i < 2 && <span className="text-stone-600">→</span>}
            </div>
          )
        })}
      </div>

      {/* Phase A: Style */}
      <div className="bg-card border border-border rounded-2xl p-5">
        <h3 className="text-sm font-semibold text-stone-300 mb-3">A. 시각 스타일 선택</h3>
        <div className="grid grid-cols-5 gap-2 mb-4">
          {STYLES.map((s) => (
            <StyleCard key={s} style={s} selected={selectedStyle === s} onClick={() => setSelectedStyle(s)} />
          ))}
        </div>
        <button
          onClick={handleStyleConfirm}
          disabled={phase !== 'style' || preparing}
          className="w-full py-2.5 rounded-xl btn-primary text-white text-sm font-medium disabled:opacity-40 flex items-center justify-center gap-2"
        >
          {preparing
            ? <><Loader size={14} className="animate-spin" />씬 분할 중...</>
            : phase !== 'style'
              ? `✓ ${selectedStyle} 선택됨`
              : `${selectedStyle} 스타일로 씬 분할 →`
          }
        </button>
      </div>

      {/* Phase B: Character */}
      {(phase === 'character' || phase === 'generate') && (
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="bg-card border border-border rounded-2xl p-5">
          <h3 className="text-sm font-semibold text-stone-300 mb-3">B. 제작 에셋 시트 — 주인공 / 조연 / 배경&아이템</h3>
          <p className="text-xs text-stone-500 mb-3">가사에서 자동 추출된 캐릭터 정보를 설정하세요</p>

          {charBasePrompt ? (
            <div className="bg-elevated rounded-xl p-3 mb-3">
              <p className="text-xs text-stone-400">현재 캐릭터: <span className="text-stone-300">{charBasePrompt}</span></p>
            </div>
          ) : (
            <div className="bg-elevated rounded-xl p-3 mb-3 text-xs text-stone-500">
              아직 캐릭터가 설정되지 않았습니다
            </div>
          )}

          <div className="flex gap-3">
            <button onClick={() => setShowCharModal(true)} className="flex-1 py-2.5 rounded-xl border border-border text-stone-400 text-sm hover:text-stone-300 hover:border-stone-500 flex items-center justify-center gap-2 transition-all">
              <User size={14} />{character ? '캐릭터 수정' : '캐릭터 설정'}
            </button>
            {character && (
              <button onClick={handleCharSheet} disabled={charSheetDone || charSheetLoading}
                className="flex-1 py-2.5 rounded-xl btn-primary text-white text-sm font-medium disabled:opacity-50 flex items-center justify-center gap-2">
                {charSheetLoading ? <><Loader size={14} className="animate-spin" />생성 중 (최대 5~10분)...</>
                  : charSheetDone ? <><CheckCircle size={14} />에셋 시트 완성</>
                  : '★ 에셋 시트 생성 (주인공+조연+배경 4K)'}
              </button>
            )}
          </div>

          {charViews.length > 0 && (
            <div className="flex gap-3 mt-3">
              {charViews.map((v) => (
                <div key={v.view} className="flex-1">
                  <div className="relative w-full aspect-square rounded-xl border border-border overflow-hidden bg-elevated">
                    <img
                      src={`/api/images/file/${v.file}?pid=${projectId}&t=${Date.now()}`}
                      alt={v.view}
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        e.target.style.display = 'none'
                        e.target.nextSibling.style.display = 'flex'
                      }}
                    />
                    <div className="absolute inset-0 hidden items-center justify-center text-xs text-stone-500 flex-col gap-1 p-2 text-center">
                      <User size={20} className="text-stone-500" />
                      <span>{v.label || v.view}</span>
                      {v.error && <span className="text-red-400 text-xs mt-1 break-all">{v.error.slice(0, 80)}</span>}
                    </div>
                  </div>
                  <p className="text-xs text-center text-stone-500 mt-1">{v.label || v.view}</p>
                </div>
              ))}
            </div>
          )}

          {/* 에셋 시트 생성 중 진행 로그 */}
          {charSheetLoading && assetLogs.length > 0 && (
            <div className="mt-3 rounded-xl bg-stone-900/50 border border-stone-700/50 p-3 space-y-1 max-h-20 overflow-y-auto">
              {assetLogs.map((log, i) => (
                <p key={i} className={`text-xs ${i === assetLogs.length - 1 ? 'text-stone-300' : 'text-stone-500'}`}>{log}</p>
              ))}
            </div>
          )}

          {/* 에셋 시트 에러 상세 */}
          {assetError && (
            <div className="mt-3 rounded-xl border border-red-500/30 bg-red-500/5 p-3 space-y-2">
              <p className="text-xs font-semibold text-red-400">
                에셋 시트 에러: {assetError.error_type}
              </p>
              <p className="text-xs text-red-300 break-all">{assetError.error}</p>
              {assetError.trace && (
                <pre className="text-[10px] text-stone-400 bg-stone-900/60 rounded p-2 overflow-auto max-h-48 whitespace-pre-wrap break-all leading-relaxed">
                  {assetError.trace}
                </pre>
              )}
              <div className="flex gap-3">
                <button
                  onClick={() => { setAssetError(null); handleCharSheet() }}
                  className="text-xs text-orange-400 hover:text-orange-300 transition-colors font-medium"
                >
                  재시도
                </button>
                <button
                  onClick={() => setAssetError(null)}
                  className="text-xs text-stone-500 hover:text-stone-300 transition-colors"
                >
                  닫기
                </button>
              </div>
            </div>
          )}

          {charBasePrompt && phase === 'character' && (
            <button onClick={() => setPhase('generate')} className="w-full mt-3 py-2.5 rounded-xl btn-primary text-white text-sm font-medium flex items-center justify-center gap-2">
              <ChevronRight size={14} />이미지 생성 방식 선택
            </button>
          )}
        </motion.div>
      )}

      {/* Phase C: Generate */}
      {phase === 'generate' && (
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="bg-card border border-border rounded-2xl p-5 space-y-4">
          <h3 className="text-sm font-semibold text-stone-300">C. 이미지 생성 방식</h3>

          <div className="grid grid-cols-2 gap-3">
            <button onClick={() => setGenerationMode('auto')}
              className={`p-4 rounded-xl border-2 text-left transition-all ${generationMode === 'auto' ? 'border-stone-400/60 bg-stone-600/20' : 'border-border bg-elevated hover:border-stone-500'}`}>
              <Zap size={20} className="text-orange-400 mb-2" />
              <p className="text-sm font-medium text-stone-300">⚡ API 자동생성</p>
              <p className="text-xs text-stone-500 mt-1">Nano Banana Pro · $0.134/장</p>
            </button>
            <button onClick={() => setGenerationMode('manual')}
              className={`p-4 rounded-xl border-2 text-left transition-all ${generationMode === 'manual' ? 'border-green-500 bg-green-500/10' : 'border-border bg-elevated hover:border-stone-500'}`}>
              <Hand size={20} className="text-green-400 mb-2" />
              <p className="text-sm font-medium text-stone-300">🆓 수동 생성</p>
              <p className="text-xs text-stone-500 mt-1">Gemini 앱 · 무료</p>
            </button>
          </div>

          {generationMode === 'auto' ? (
            <>
              <div className="bg-stone-700/30 border border-stone-600/40 rounded-xl px-4 py-3 flex justify-between items-center">
                <span className="text-sm text-stone-300">{scenes?.length || 0}장 · 씬 간 8초 딜레이 포함</span>
                <span className="text-amber-400 font-mono font-semibold">최대 ${((scenes?.length || 0) * 0.134).toFixed(2)}</span>
              </div>
              <button onClick={handleAutoGenerate} disabled={running || isOverLimit}
                className="w-full py-4 rounded-2xl btn-primary text-white font-semibold flex items-center justify-center gap-2">
                {running ? (
                  <><div className="flex gap-1">{[0,1,2,3,4].map(i => <span key={i} className="wave-bar h-5" style={{ animationDelay: `${i*0.15}s` }} />)}</div>생성 중...</>
                ) : (
                  <><Image size={18} />이미지 자동 생성</>
                )}
              </button>
              {(running || logs.length > 0) && <ProgressBar logs={logs} running={running} />}
            </>
          ) : (
            <div className="space-y-3">
              <p className="text-xs text-stone-500">각 씬의 Gemini 프롬프트를 복사해서 직접 생성하세요</p>
              {scenes?.map((scene, i) => (
                <div key={i} className={`rounded-xl border p-3 ${scene.is_chorus ? 'border-yellow-500/40 bg-yellow-500/5' : 'border-border bg-elevated'}`}>
                  <div className="flex justify-between items-start gap-2">
                    <div>
                      <p className="text-xs text-stone-500">{scene.section} {scene.is_chorus && '⭐'}</p>
                      <p className="text-xs text-stone-400 mt-0.5 line-clamp-2">{charBasePrompt}, {scene.description}</p>
                    </div>
                    <button onClick={() => { navigator.clipboard.writeText(`${charBasePrompt}, ${scene.description}, ${selectedStyle} style`); toast.success('복사됨!') }}
                      className="shrink-0 p-1.5 rounded-lg bg-card text-stone-500 hover:text-stone-300">
                      <Copy size={12} />
                    </button>
                  </div>
                </div>
              ))}
              <a href="https://gemini.google.com" target="_blank" rel="noopener noreferrer"
                className="flex items-center justify-center gap-2 py-2.5 rounded-xl border border-border text-stone-400 text-sm hover:text-stone-300 transition-all">
                <ExternalLink size={14} />Gemini 앱 열기
              </a>
            </div>
          )}
        </motion.div>
      )}

      {/* Result */}
      {generatedScenes.length > 0 && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-3">
          <h3 className="text-sm font-semibold text-stone-300 flex items-center justify-between">
            생성된 이미지
            {genSummary && (
              <span className="text-xs font-normal">
                <span className="text-green-400">✓ {genSummary.success}개</span>
                {genSummary.failed > 0 && <span className="text-red-400 ml-2">✗ {genSummary.failed}개</span>}
              </span>
            )}
          </h3>

          {/* 실패 씬 재생성 배너 */}
          {genSummary?.failed > 0 && (
            <div className="flex items-center justify-between bg-yellow-500/10 border border-yellow-500/30 rounded-xl px-4 py-3">
              <span className="text-sm text-yellow-400">⚠️ 실패한 씬 {genSummary.failed}개 (속도 제한으로 플레이스홀더 사용)</span>
              <button
                onClick={handleRetryFailed}
                disabled={retryRunning || isOverLimit}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-yellow-500/20 text-yellow-300 text-xs font-medium hover:bg-yellow-500/30 transition-all disabled:opacity-50"
              >
                {retryRunning ? <><Loader size={12} className="animate-spin" />재생성 중...</> : <><RefreshCw size={12} />실패한 씬만 다시 생성</>}
              </button>
            </div>
          )}

          {retryRunning && <ProgressBar logs={logs} running={retryRunning} />}

          <SceneGrid scenes={generatedScenes} projectId={projectId} type="image" />
          <button onClick={handleConfirm} disabled={running || retryRunning}
            className="w-full py-4 rounded-2xl btn-primary text-white font-semibold flex items-center justify-center gap-2 disabled:opacity-50">
            확정 → 영상 생성<ChevronRight size={16} />
          </button>
        </motion.div>
      )}

      {phase === 'generate' && generatedScenes.length === 0 && !running && generationMode === 'manual' && (
        <button onClick={handleConfirm} className="w-full py-4 rounded-2xl btn-primary text-white font-semibold flex items-center justify-center gap-2">
          확정 → 영상 생성<ChevronRight size={16} />
        </button>
      )}
    </div>
  )
}
