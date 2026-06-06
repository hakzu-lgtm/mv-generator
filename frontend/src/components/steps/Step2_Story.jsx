import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { BookOpen, RefreshCw, ChevronRight, Star, User, MapPin, Sparkles, Loader } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../../api/client'
import useProjectStore from '../../store/projectStore'

export default function Step2_Story() {
  const { projectId, story, setStory, setStep, markStepComplete } = useProjectStore()
  const [loading, setLoading]   = useState(false)
  const [autoRan, setAutoRan]   = useState(false)

  // 가사 확정 후 자동 생성
  useEffect(() => {
    if (!story && !autoRan && !loading) {
      setAutoRan(true)
      handleGenerate()
    }
  }, [])

  const handleGenerate = async () => {
    setLoading(true)
    try {
      const res = await api.post('/story/generate', { project_id: projectId }, { timeout: 60000 })
      setStory(res.data)
      toast.success('스토리 생성 완료!')
    } catch (e) {
      toast.error(`스토리 생성 실패: ${e.message}`)
    } finally {
      setLoading(false)
    }
  }

  const handleConfirm = async () => {
    if (!story) { toast.error('스토리를 먼저 생성해주세요'); return }
    try {
      await api.post('/story/confirm', { project_id: projectId, story_data: story })
      markStepComplete(2)
      setStep(3)
      toast.success('스토리 확정! 음악 생성으로 이동합니다')
    } catch (e) {
      toast.error(e.message)
    }
  }

  const ArcCard = ({ label, content, color }) => (
    <div className={`flex-1 min-w-0 rounded-xl border p-3 ${color}`}>
      <p className="text-xs font-bold mb-1">{label}</p>
      <p className="text-xs text-stone-300 leading-relaxed">{content}</p>
    </div>
  )

  return (
    <div className="max-w-3xl mx-auto space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-stone-200 flex items-center gap-2">
            <BookOpen size={22} className="text-amber-400" />스토리
          </h2>
          <p className="text-stone-500 text-sm mt-0.5">가사에서 뮤직비디오 서사를 생성합니다 · Gemini · 무료</p>
        </div>
        <span className="px-2.5 py-1 rounded-full bg-green-500/20 text-green-400 text-xs border border-green-500/30">FREE</span>
      </div>

      {loading && (
        <div className="bg-card border border-border rounded-2xl p-8 text-center">
          <Loader size={32} className="animate-spin text-amber-400 mx-auto mb-3" />
          <p className="text-stone-400 text-sm">가사를 분석해 스토리를 구성 중...</p>
        </div>
      )}

      {!loading && !story && (
        <div className="bg-card border border-border rounded-2xl p-8 text-center">
          <BookOpen size={32} className="text-stone-500 mx-auto mb-3" />
          <p className="text-stone-500 text-sm mb-4">스토리가 아직 생성되지 않았습니다</p>
          <button onClick={handleGenerate} className="px-6 py-2.5 rounded-xl btn-primary text-white text-sm font-medium flex items-center gap-2 mx-auto">
            <Sparkles size={14} />스토리 생성
          </button>
        </div>
      )}

      {story && !loading && (
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
          {/* 로그라인 */}
          <div className="bg-amber-500/10 border border-amber-500/30 rounded-2xl p-4">
            <p className="text-xs text-amber-400 font-medium mb-1">로그라인</p>
            <p className="text-stone-200 font-medium">{story.logline}</p>
            {story.theme && <p className="text-xs text-stone-500 mt-1">주제: {story.theme}</p>}
          </div>

          {/* 기승전결 */}
          <div className="bg-card border border-border rounded-2xl p-4">
            <p className="text-xs text-stone-500 font-medium mb-3 uppercase tracking-wider">기승전결</p>
            <div className="flex gap-2 flex-wrap sm:flex-nowrap">
              <ArcCard label="기 (도입)" content={story.arc?.기} color="border-stone-500/30 bg-stone-700/20" />
              <ArcCard label="승 (고조)" content={story.arc?.승} color="border-amber-500/30 bg-amber-500/5" />
              <ArcCard label="전 (전환)" content={story.arc?.전} color="border-yellow-500/30 bg-yellow-500/5" />
              <ArcCard label="결 (해소)" content={story.arc?.결} color="border-green-500/30 bg-green-500/5" />
            </div>
          </div>

          {/* 등장인물 */}
          {story.characters && (
            <div className="bg-card border border-border rounded-2xl p-4">
              <p className="text-xs text-stone-500 font-medium mb-3 uppercase tracking-wider flex items-center gap-1.5">
                <User size={12} />등장인물
              </p>
              <div className="grid grid-cols-2 gap-3">
                {story.characters.protagonist && (
                  <div className="bg-elevated rounded-xl p-3">
                    <p className="text-xs font-bold text-orange-400 mb-1">주인공 · {story.characters.protagonist.name}</p>
                    <p className="text-xs text-stone-400 leading-relaxed">{story.characters.protagonist.description}</p>
                    {story.characters.protagonist.arc && (
                      <p className="text-xs text-stone-500 mt-1 italic">변화: {story.characters.protagonist.arc}</p>
                    )}
                  </div>
                )}
                {story.characters.supporting && (
                  <div className="bg-elevated rounded-xl p-3">
                    <p className="text-xs font-bold text-amber-400 mb-1">조연 · {story.characters.supporting.name}</p>
                    <p className="text-xs text-stone-400 leading-relaxed">{story.characters.supporting.description}</p>
                    {story.characters.supporting.role && (
                      <p className="text-xs text-stone-500 mt-1 italic">역할: {story.characters.supporting.role}</p>
                    )}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* 배경 & 아이템 */}
          {(story.settings?.length || story.items?.length) && (
            <div className="bg-card border border-border rounded-2xl p-4">
              <p className="text-xs text-stone-500 font-medium mb-3 uppercase tracking-wider flex items-center gap-1.5">
                <MapPin size={12} />배경 & 소품
              </p>
              <div className="flex gap-2 flex-wrap">
                {story.settings?.map(s => (
                  <span key={s.id} className="px-2.5 py-1 rounded-full bg-elevated border border-border text-xs text-stone-300">
                    {s.name}
                  </span>
                ))}
                {story.items?.map(it => (
                  <span key={it.id} className="px-2.5 py-1 rounded-full bg-elevated border border-yellow-500/20 text-xs text-yellow-400">
                    {it.name}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* 훅 모티프 */}
          {story.hook_motif && (
            <div className="flex items-start gap-3 bg-yellow-500/10 border border-yellow-500/30 rounded-xl px-4 py-3">
              <Star size={16} className="text-yellow-400 shrink-0 mt-0.5" fill="currentColor" />
              <div>
                <p className="text-xs text-yellow-400 font-bold mb-0.5">반복 훅 모티프 (코러스마다 등장)</p>
                <p className="text-xs text-stone-300">{story.hook_motif}</p>
              </div>
            </div>
          )}

          {/* 씬 플랜 */}
          {story.scene_plan?.length > 0 && (
            <div className="bg-card border border-border rounded-2xl p-4">
              <p className="text-xs text-stone-500 font-medium mb-3 uppercase tracking-wider">장면 계획</p>
              <div className="space-y-2 max-h-64 overflow-y-auto pr-1">
                {story.scene_plan.map((sp, i) => (
                  <div key={i} className={`flex items-start gap-2 rounded-lg px-3 py-2 text-xs ${
                    sp.is_chorus ? 'bg-yellow-500/10 border border-yellow-500/20' : 'bg-elevated'
                  }`}>
                    {sp.is_chorus && <Star size={10} className="text-yellow-400 shrink-0 mt-0.5" fill="currentColor" />}
                    <span className={`shrink-0 font-medium w-16 ${sp.is_chorus ? 'text-yellow-400' : 'text-stone-500'}`}>
                      {sp.section}
                    </span>
                    <span className="text-stone-400 leading-relaxed">{sp.beat}</span>
                    {sp.use_hook_motif && (
                      <span className="ml-auto shrink-0 text-yellow-400 text-xs">훅</span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="flex gap-3 pt-2">
            <button onClick={handleGenerate} disabled={loading}
              className="flex-1 py-3 rounded-xl border border-border text-stone-400 hover:text-stone-300 flex items-center justify-center gap-2 text-sm transition-all">
              <RefreshCw size={14} />재생성
            </button>
            <button onClick={handleConfirm}
              className="flex-1 py-3 rounded-xl btn-primary text-white font-semibold text-sm flex items-center justify-center gap-2">
              이 스토리로 진행 →<ChevronRight size={16} />
            </button>
          </div>
        </motion.div>
      )}
    </div>
  )
}
