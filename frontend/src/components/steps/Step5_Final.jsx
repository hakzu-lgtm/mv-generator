import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Film, Download, Share2, RefreshCw, Layers,
  FolderOpen, CheckCircle, Loader, Copy, Info,
} from 'lucide-react'
import ReactConfetti from 'react-confetti'
import toast from 'react-hot-toast'
import api, { postSSE } from '../../api/client'
import useProjectStore from '../../store/projectStore'
import VideoPlayer from '../ui/VideoPlayer'
import ProgressBar from '../ui/ProgressBar'
import { useCostGuard } from '../../hooks/useCostGuard'

const TRANSITIONS = ['fade', 'cut', 'slide']

const CAPCUT_PATH_WIN = '%LOCALAPPDATA%\\CapCut\\User Data\\Projects\\com.lveditor.draft\\'
const CAPCUT_PATH_MAC = '~/Movies/CapCut/User Data/Projects/com.lveditor.draft/'

export default function Step5_Final() {
  const { projectId, resetProject } = useProjectStore()
  const { sessionCost, breakdown, refreshCost } = useCostGuard()

  // 설정
  const [transition, setTransition] = useState('fade')

  // 출력 방식 선택
  const [outputMode, setOutputMode] = useState(null)  // null | 'mp4' | 'capcut'

  // MP4 상태
  const [mp4Running, setMp4Running]   = useState(false)
  const [mp4Logs, setMp4Logs]         = useState([])
  const [mp4Result, setMp4Result]     = useState(null)
  const [mp4Error, setMp4Error]       = useState(null)

  // CapCut 상태
  const [ccRunning, setCcRunning]     = useState(false)
  const [ccSteps, setCcSteps]         = useState([])
  const [ccResult, setCcResult]       = useState(null)

  const [showConfetti, setShowConfetti] = useState(false)

  // ── MP4 합성 ────────────────────────────────────────────────────
  const handleMp4Generate = async () => {
    setMp4Running(true)
    setMp4Logs([])
    setMp4Result(null)
    setMp4Error(null)

    await postSSE(
      '/api/final/generate',
      { project_id: projectId },
      (data) => setMp4Logs((l) => [...l, { ...data, time: Date.now() }]),
      (err)  => { setMp4Error(err.message); setMp4Running(false) },
      async (data) => {
        setMp4Result(data)
        await refreshCost()
        setMp4Running(false)
        setShowConfetti(true)
        toast.success('🎉 뮤직비디오 완성!')
        setTimeout(() => setShowConfetti(false), 6000)
      }
    )
  }

  // ── CapCut 생성 ─────────────────────────────────────────────────
  const CC_STEP_MSGS = [
    '클립 타임라인 구성 중...',
    '음악 트랙 배치 중...',
    '가사 자막 추가 중...',
    'Draft 폴더 압축 중...',
  ]

  const handleCapcutGenerate = async () => {
    setCcRunning(true)
    setCcSteps([])
    setCcResult(null)

    // 진행 단계 시뮬레이션 (실제 처리는 백엔드)
    for (let i = 0; i < CC_STEP_MSGS.length - 1; i++) {
      setCcSteps((s) => [...s, { msg: CC_STEP_MSGS[i], done: false }])
      await new Promise((r) => setTimeout(r, 400))
      setCcSteps((s) => s.map((x, idx) => idx === i ? { ...x, done: true } : x))
    }
    setCcSteps((s) => [...s, { msg: CC_STEP_MSGS[CC_STEP_MSGS.length - 1], done: false }])

    try {
      const res = await api.post(`/final/capcut/${projectId}`)
      setCcSteps((s) => s.map((x, i) => i === s.length - 1 ? { ...x, done: true } : x))
      setCcResult(res.data)
      setShowConfetti(true)
      toast.success('🎉 CapCut 프로젝트 준비 완료!')
      setTimeout(() => setShowConfetti(false), 6000)
    } catch (e) {
      toast.error(e.message)
    } finally {
      setCcRunning(false)
    }
  }

  const copyPath = (path) => {
    navigator.clipboard.writeText(path)
    toast.success('경로 복사됨!')
  }

  // ── 비용 요약 ────────────────────────────────────────────────────
  const musicCost  = Object.entries(breakdown).filter(([k]) => k.startsWith('lyria')).reduce((s, [, v]) => s + v, 0)
  const imageCost  = Object.entries(breakdown).filter(([k]) => k.startsWith('image')).reduce((s, [, v]) => s + v, 0)
  const videoCost  = Object.entries(breakdown).filter(([k]) => k.startsWith('veo')).reduce((s, [, v]) => s + v, 0)

  const CostSummary = () => (
    <div className="bg-card border border-border rounded-2xl p-5">
      <h3 className="text-sm font-semibold text-stone-300 mb-3 flex items-center gap-2">
        <Layers size={14} className="text-orange-400" />비용 최종 요약
      </h3>
      <div className="space-y-1.5 text-sm">
        {[
          ['① 가사 (Gemini)', null, true],
          ['② 스토리 (Gemini)', null, true],
          ['③ 음악 (Lyria)', musicCost, false],
          ['④ 이미지 (Nano Banana)', imageCost, false],
          ['⑤ 영상 (Veo)', videoCost, false],
          ['⑥ 최종 편집 (FFmpeg / CapCut)', null, true],
        ].map(([label, cost, isFree]) => (
          <div key={label} className="flex justify-between text-stone-400">
            <span>{label}</span>
            <span className={isFree ? 'text-green-400' : 'text-stone-300 font-mono'}>
              {isFree ? '무료' : cost > 0 ? `$${cost.toFixed(3)}` : '-'}
            </span>
          </div>
        ))}
        <div className="border-t border-border pt-2 flex justify-between font-semibold">
          <span className="text-stone-300">세션 합계</span>
          <span className="text-orange-400 font-mono">${sessionCost.toFixed(2)}</span>
        </div>
        <div className="flex justify-between text-xs text-stone-500">
          <span>남은 안전 크레딧</span>
          <span>${Math.max(0, 250 - sessionCost).toFixed(2)}</span>
        </div>
      </div>
    </div>
  )

  // ── 편집 설정 패널 ───────────────────────────────────────────────
  const SettingsPanel = () => (
    <div className="bg-card border border-border rounded-2xl p-5 space-y-4">
      <h3 className="text-sm font-semibold text-stone-300">편집 설정</h3>

      <div className="bg-stone-700/30 border border-stone-600/40 rounded-xl px-4 py-3 text-xs text-stone-400 leading-relaxed">
        자막은 포함되지 않습니다. 완성 후 CapCut에서 자막을 직접 추가하세요.
      </div>
    </div>
  )

  return (
    <div className="max-w-2xl mx-auto space-y-6 animate-fade-in">
      {showConfetti && (
        <ReactConfetti
          width={window.innerWidth} height={window.innerHeight}
          recycle={false} numberOfPieces={400}
          colors={['#3B82F6', '#6366F1', '#F59E0B', '#10B981']}
        />
      )}

      <div>
        <h2 className="text-2xl font-bold text-stone-200">최종 편집</h2>
        <p className="text-stone-500 text-sm mt-0.5">출력 방식을 선택하세요</p>
      </div>

      <CostSummary />
      <SettingsPanel />

      {/* ── 출력 방식 선택 카드 ──────────────────────────────────── */}
      {!outputMode && (
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
          <p className="text-sm font-semibold text-stone-300 mb-3">📤 결과물 형식을 선택하세요</p>
          <div className="grid grid-cols-2 gap-4">

            {/* MP4 카드 */}
            <button
              onClick={() => setOutputMode('mp4')}
              className="group p-5 rounded-2xl border-2 border-border bg-card hover:border-stone-500/60 hover:bg-stone-700/20 text-left transition-all"
            >
              <Film size={28} className="text-orange-400 mb-3" />
              <p className="font-semibold text-stone-200 text-sm">🎬 완성 영상</p>
              <p className="text-xs text-stone-500 mt-1 leading-relaxed">
                바로 재생·공유 가능한<br/>MP4 파일
              </p>
              <ul className="mt-3 space-y-1 text-xs text-stone-500">
                <li>· 즉시 사용 가능</li>
                <li>· 추가 앱 불필요</li>
                <li>· 수정 불가</li>
              </ul>
              <div className="mt-4 py-2 rounded-xl bg-stone-600/30 text-stone-300 text-xs font-medium text-center">
                MP4로 만들기
              </div>
            </button>

            {/* CapCut 카드 */}
            <button
              onClick={() => setOutputMode('capcut')}
              className="group p-5 rounded-2xl border-2 border-amber-500/40 bg-amber-500/5 hover:border-amber-500/80 hover:bg-amber-500/10 text-left transition-all relative"
            >
              <div className="absolute top-3 right-3 px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-400 text-xs font-bold">
                ⭐ 추천
              </div>
              <FolderOpen size={28} className="text-amber-400 mb-3" />
              <p className="font-semibold text-stone-200 text-sm">📁 CapCut 프로젝트</p>
              <p className="text-xs text-stone-500 mt-1 leading-relaxed">
                CapCut에서 직접<br/>편집·수정 가능
              </p>
              <ul className="mt-3 space-y-1 text-xs text-stone-500">
                <li>· 자유로운 편집</li>
                <li>· 무료, 인코딩 없음</li>
                <li>· CapCut 앱 필요</li>
              </ul>
              <div className="mt-4 py-2 rounded-xl bg-amber-500/20 text-amber-300 text-xs font-medium text-center">
                CapCut으로 →
              </div>
            </button>
          </div>
        </motion.div>
      )}

      {/* ── 선택 변경 버튼 ───────────────────────────────────────── */}
      {outputMode && !mp4Result && !ccResult && (
        <button onClick={() => setOutputMode(null)}
          className="text-xs text-stone-500 hover:text-stone-400 transition-colors">
          ← 출력 방식 다시 선택
        </button>
      )}

      {/* ══ MP4 경로 ════════════════════════════════════════════════ */}
      <AnimatePresence>
        {outputMode === 'mp4' && !mp4Result && (
          <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
            <button
              onClick={handleMp4Generate}
              disabled={mp4Running}
              className="w-full py-4 rounded-2xl btn-primary text-white font-semibold text-base flex items-center justify-center gap-2"
            >
              {mp4Running
                ? <><div className="flex gap-1">{[0,1,2,3,4].map(i=><span key={i} className="wave-bar h-5" style={{animationDelay:`${i*0.15}s`}}/>)}</div>합성 중...</>
                : <><Film size={18}/>🎬 최종 합성 시작 (무료)</>
              }
            </button>
            {(mp4Running || mp4Logs.length > 0) && <ProgressBar logs={mp4Logs} running={mp4Running} />}
            {mp4Error && (
              <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4">
                <p className="text-red-400 text-xs font-bold mb-2">FFmpeg 에러 (전체)</p>
                <pre className="text-xs text-red-300 whitespace-pre-wrap overflow-auto max-h-64 font-mono leading-relaxed">
                  {mp4Error}
                </pre>
                <p className="text-xs text-stone-500 mt-2">위 에러를 복사해서 원인을 확인하세요.</p>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* MP4 완료 */}
      {mp4Result && (
        <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="space-y-4">
          <div className="text-center py-4">
            <div className="text-5xl mb-2">🎊</div>
            <h3 className="text-xl font-bold gradient-text">뮤직비디오 완성!</h3>
            <div className="flex items-center justify-center gap-4 mt-2 text-xs text-stone-500">
              <span>📦 {mp4Result.size_mb}MB</span>
              <span>🎬 {mp4Result.clips}씬</span>
              <span>💰 ${sessionCost.toFixed(2)}</span>
            </div>
          </div>
          <VideoPlayer
            src={`/api/final/preview/${projectId}`}
            title={`뮤직비디오 · ${mp4Result.clips}씬`}
            fileSize={mp4Result.size_mb}
            clipCount={mp4Result.clips}
          />
          <div className="flex gap-3">
            <a href={`/api/final/download/${projectId}`} download
              className="flex-1 py-3 rounded-xl btn-primary text-white font-semibold text-sm flex items-center justify-center gap-2">
              <Download size={14}/>⬇️ 다운로드
            </a>
            <button onClick={() => { navigator.clipboard.writeText(window.location.href); toast.success('링크 복사됨!') }}
              className="py-3 px-4 rounded-xl border border-border text-stone-400 hover:text-stone-300 flex items-center gap-2 text-sm transition-all">
              <Share2 size={14}/>📤 공유
            </button>
          </div>
          <div className="flex gap-3">
            <button onClick={() => toast('📱 Shorts 변환: FFmpeg로 세로형(9:16) 변환은 백엔드 /api/final/shorts 엔드포인트 연결 후 지원 예정입니다.', { duration: 4000 })}
              className="flex-1 py-2.5 rounded-xl border border-border text-stone-500 text-xs flex items-center justify-center gap-1.5 hover:text-stone-300 transition-all">
              📱 세로형 Shorts 변환
            </button>
            <button onClick={() => { if(confirm('새 프로젝트를 시작하시겠습니까?')) { resetProject(); toast.success('새 프로젝트!') } }}
              className="flex-1 py-2.5 rounded-xl border border-border text-stone-500 text-xs flex items-center justify-center gap-1.5 hover:text-stone-300 transition-all">
              <RefreshCw size={12}/>🔄 새 프로젝트
            </button>
          </div>
        </motion.div>
      )}

      {/* ══ CapCut 경로 ════════════════════════════════════════════ */}
      <AnimatePresence>
        {outputMode === 'capcut' && !ccResult && (
          <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="space-y-4">

            {/* 진행 상황 */}
            {ccRunning && (
              <div className="bg-card border border-border rounded-2xl p-5 space-y-3">
                <p className="text-sm font-medium text-stone-300 flex items-center gap-2">
                  <Loader size={14} className="animate-spin text-amber-400" />
                  CapCut 프로젝트 생성 중...
                </p>
                {ccSteps.map((step, i) => (
                  <div key={i} className="flex items-center gap-2 text-sm">
                    {step.done
                      ? <CheckCircle size={14} className="text-green-400 shrink-0" />
                      : <Loader size={14} className="animate-spin text-amber-400 shrink-0" />
                    }
                    <span className={step.done ? 'text-stone-400' : 'text-stone-300'}>{step.msg}</span>
                  </div>
                ))}
              </div>
            )}

            {!ccRunning && (
              <button
                onClick={handleCapcutGenerate}
                className="w-full py-4 rounded-2xl bg-gradient-to-r from-amber-600 to-amber-500 hover:opacity-90 text-white font-semibold text-base flex items-center justify-center gap-2 transition-all"
              >
                <FolderOpen size={18}/>📁 CapCut 프로젝트 생성 (무료)
              </button>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* CapCut 완료 */}
      {ccResult && (
        <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="space-y-4">
          <div className="text-center py-4">
            <div className="text-5xl mb-2">🎊</div>
            <h3 className="text-xl font-bold text-amber-300">CapCut 프로젝트 준비됐어요!</h3>
            <p className="text-xs text-stone-500 mt-1">폴더명: <code className="text-amber-400">{ccResult.draft_name}</code></p>
          </div>

          <a href={`/api/final/capcut/download/${projectId}`} download="capcut_project.zip"
            className="flex items-center justify-center gap-2 w-full py-4 rounded-2xl bg-gradient-to-r from-amber-600 to-amber-500 text-white font-semibold text-base hover:opacity-90 transition-all">
            <Download size={18}/>⬇️ CapCut 프로젝트 다운로드 (ZIP)
          </a>

          {/* 사용 방법 */}
          <div className="bg-card border border-border rounded-2xl p-5 space-y-4">
            <h4 className="text-sm font-semibold text-stone-300 flex items-center gap-2">
              <Info size={14} className="text-amber-400"/>📌 사용 방법
            </h4>
            <ol className="space-y-2 text-sm text-stone-400 list-decimal list-inside">
              <li>ZIP 파일 압축 해제</li>
              <li><code className="text-amber-400">{ccResult.draft_name}</code> 폴더를 아래 경로에 복사</li>
              <li>CapCut 실행 → 프로젝트 목록에 표시됨</li>
              <li>열어서 자유롭게 편집!</li>
            </ol>

            <div className="space-y-2">
              {[
                { os: '🪟 Windows', path: CAPCUT_PATH_WIN },
                { os: '🍎 Mac', path: CAPCUT_PATH_MAC },
              ].map(({ os, path }) => (
                <div key={os} className="bg-elevated rounded-xl p-3">
                  <p className="text-xs text-stone-500 mb-1.5">{os}</p>
                  <div className="flex items-center gap-2">
                    <code className="flex-1 text-xs text-amber-300 break-all">{path}</code>
                    <button onClick={() => copyPath(path)}
                      className="shrink-0 p-1.5 rounded-lg bg-card text-stone-500 hover:text-stone-300 transition-colors">
                      <Copy size={12}/>
                    </button>
                  </div>
                </div>
              ))}
            </div>

            {/* 주의사항 */}
            <div className="space-y-2 pt-1">
              <p className="text-xs text-stone-500 leading-relaxed">
                💡 CapCut 버전에 따라 일부 전환·자막 스타일이 다르게 표시될 수 있습니다.
                클립·음악·자막 텍스트는 정상적으로 불러와집니다.
              </p>
              <p className="text-xs text-yellow-600/80 leading-relaxed">
                ⚠️ draft 폴더를 복사하기 전에 CapCut을 완전히 종료하세요.
                실행 중에는 새 프로젝트가 인식되지 않을 수 있습니다.
              </p>
            </div>
          </div>

          <div className="flex gap-3">
            <button onClick={() => copyPath(CAPCUT_PATH_WIN)}
              className="flex-1 py-2.5 rounded-xl border border-border text-stone-500 text-xs flex items-center justify-center gap-1.5 hover:text-stone-300 transition-all">
              <Copy size={12}/>📋 Windows 경로 복사
            </button>
            <button onClick={() => { if(confirm('새 프로젝트를 시작하시겠습니까?')) { resetProject(); toast.success('새 프로젝트!') } }}
              className="flex-1 py-2.5 rounded-xl border border-border text-stone-500 text-xs flex items-center justify-center gap-1.5 hover:text-stone-300 transition-all">
              <RefreshCw size={12}/>🔄 새 프로젝트
            </button>
          </div>
        </motion.div>
      )}
    </div>
  )
}
