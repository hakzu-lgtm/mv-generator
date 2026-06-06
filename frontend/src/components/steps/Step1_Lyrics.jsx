import { useState } from 'react'
import { motion } from 'framer-motion'
import { Sparkles, RefreshCw, ChevronRight, Star, Edit2, Check } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../../api/client'
import useProjectStore from '../../store/projectStore'
import GenreCard from '../ui/GenreCard'

const GENRES = ['트롯트', 'K-POP', '댄스', 'K-힙합', '발라드', '인디팝', '시티팝', '신스팝', '시네마틱', '어쿠스틱', '재즈', '록']
const INSTRUMENTS = ['피아노', '신시사이저', '기타', '베이스', '드럼', '현악기', '관악기', '전자피아노', '우쿨렐레', '트럼펫']
const GENDERS = ['여성', '남성', '혼성']
const AGES = ['10대', '20대', '30대', '40대 이상']
const STYLES = ['청아한', '허스키한', '파워풀', '감성적', '랩', '소울풀', '귀여운', '카리스마틱']
const EXAMPLE_THEMES = ['도시를 떠나 자유를 찾는 청년', '첫사랑의 설렘과 두근거림', '비 오는 날의 그리움', '우리가 함께한 모든 순간', '새벽 혼자 걷는 거리']

export default function Step1_Lyrics() {
  const { projectId, lyricsConfig, setLyricsConfig, setLyrics, lyrics, setStep, markStepComplete } = useProjectStore()
  const [loading, setLoading] = useState(false)
  const [editingIndex, setEditingIndex] = useState(null)
  const [editText, setEditText] = useState('')

  const cfg = lyricsConfig

  const toggleGenre = (g) => {
    const current = cfg.genre || []
    setLyricsConfig({
      genre: current.includes(g) ? current.filter((x) => x !== g) : [...current, g],
    })
  }

  const toggleInstrument = (inst) => {
    const current = cfg.music?.instruments || []
    setLyricsConfig({
      music: {
        ...cfg.music,
        instruments: current.includes(inst) ? current.filter((x) => x !== inst) : [...current, inst],
      },
    })
  }

  const handleGenerate = async () => {
    if (!cfg.theme) { toast.error('스토리/테마를 입력해주세요'); return }
    if (!cfg.genre?.length) { toast.error('장르를 선택해주세요'); return }

    setLoading(true)
    try {
      const res = await api.post('/lyrics/generate', {
        project_id: projectId,
        genre: cfg.genre,
        vocalist: cfg.vocalist,
        music: cfg.music,
        theme: cfg.theme,
      })
      setLyrics(res.data)
      toast.success('가사 생성 완료!')
    } catch (e) {
      toast.error(e.message)
    } finally {
      setLoading(false)
    }
  }

  const handleRegenerate = async () => {
    await handleGenerate()
  }

  const startEdit = (i, text) => {
    setEditingIndex(i)
    setEditText(text)
  }

  const saveEdit = async (i) => {
    if (!lyrics) return
    try {
      const updated = { ...lyrics }
      updated.lyrics[i].text = editText
      await api.post('/lyrics/confirm', { project_id: projectId, lyrics_data: updated })
      setLyrics(updated)
      toast.success('수정 저장됨')
    } catch (e) {
      toast.error(e.message)
    }
    setEditingIndex(null)
  }

  const handleConfirm = async () => {
    if (!lyrics) { toast.error('가사를 먼저 생성해주세요'); return }
    try {
      await api.post('/lyrics/confirm', { project_id: projectId, lyrics_data: lyrics })
      markStepComplete(1)
      setStep(2)
      toast.success('가사 확정! 음악 생성으로 이동합니다')
    } catch (e) {
      toast.error(e.message)
    }
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-stone-200">가사 생성</h2>
          <p className="text-stone-500 text-sm mt-0.5">어떤 스토리의 노래를 만들까요?</p>
        </div>
        <span className="px-2.5 py-1 rounded-full bg-green-500/20 text-green-400 text-xs font-medium border border-green-500/30">
          FREE
        </span>
      </div>

      {/* Section 1: Genre */}
      <div className="bg-card border border-border rounded-2xl p-5">
        <h3 className="text-sm font-semibold text-stone-300 mb-3">장르 선택 (복수)</h3>
        <div className="grid grid-cols-4 gap-2">
          {GENRES.map((g) => (
            <GenreCard key={g} genre={g} selected={cfg.genre?.includes(g)} onClick={() => toggleGenre(g)} />
          ))}
        </div>
      </div>

      {/* Section 2: Vocalist */}
      <div className="bg-card border border-border rounded-2xl p-5">
        <h3 className="text-sm font-semibold text-stone-300 mb-3">가수 설정</h3>
        <div className="space-y-3">
          <div>
            <label className="text-xs text-stone-500 mb-1.5 block">성별</label>
            <div className="flex gap-2">
              {GENDERS.map((g) => (
                <button key={g} onClick={() => setLyricsConfig({ vocalist: { ...cfg.vocalist, gender: g } })}
                  className={`px-3 py-1.5 rounded-lg text-xs border transition-all ${cfg.vocalist?.gender === g ? 'border-stone-400/60 bg-stone-600/20 text-stone-200' : 'border-border text-stone-500 hover:border-stone-500'}`}>
                  {g}
                </button>
              ))}
            </div>
          </div>
          <div>
            <label className="text-xs text-stone-500 mb-1.5 block">나이대</label>
            <div className="flex gap-2 flex-wrap">
              {AGES.map((a) => (
                <button key={a} onClick={() => setLyricsConfig({ vocalist: { ...cfg.vocalist, age: a } })}
                  className={`px-3 py-1.5 rounded-lg text-xs border transition-all ${cfg.vocalist?.age === a ? 'border-stone-400/60 bg-stone-600/20 text-stone-200' : 'border-border text-stone-500 hover:border-stone-500'}`}>
                  {a}
                </button>
              ))}
            </div>
          </div>
          <div>
            <label className="text-xs text-stone-500 mb-1.5 block">보컬 스타일</label>
            <div className="flex gap-2 flex-wrap">
              {STYLES.map((s) => (
                <button key={s} onClick={() => setLyricsConfig({ vocalist: { ...cfg.vocalist, style: s } })}
                  className={`px-3 py-1.5 rounded-lg text-xs border transition-all ${cfg.vocalist?.style === s ? 'border-stone-400/60 bg-stone-600/20 text-stone-200' : 'border-border text-stone-500 hover:border-stone-500'}`}>
                  {s}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Section 3: Music */}
      <div className="bg-card border border-border rounded-2xl p-5">
        <h3 className="text-sm font-semibold text-stone-300 mb-3">음악 설정</h3>
        <div className="space-y-3">
          <div>
            <label className="text-xs text-stone-500 mb-1 block flex justify-between">
              <span>템포</span>
              <span className="text-orange-400 font-mono">{cfg.music?.bpm || 120} BPM</span>
            </label>
            <input
              type="range" min="60" max="200"
              value={cfg.music?.bpm || 120}
              onChange={(e) => setLyricsConfig({ music: { ...cfg.music, bpm: parseInt(e.target.value) } })}
              className="w-full accent-orange-500"
            />
            <div className="flex justify-between text-xs text-stone-500 mt-1">
              <span>느리게 60</span><span>보통 120</span><span>빠르게 200</span>
            </div>
          </div>
          <div>
            <label className="text-xs text-stone-500 mb-1.5 block">악기 (복수 선택)</label>
            <div className="flex gap-2 flex-wrap">
              {INSTRUMENTS.map((inst) => (
                <button key={inst}
                  onClick={() => toggleInstrument(inst)}
                  className={`px-2.5 py-1 rounded-lg text-xs border transition-all ${cfg.music?.instruments?.includes(inst) ? 'border-stone-400/60 bg-stone-600/20 text-stone-200' : 'border-border text-stone-500 hover:border-stone-500'}`}>
                  {inst}
                </button>
              ))}
            </div>
          </div>
          <div className="flex items-center gap-2 p-3 bg-elevated rounded-xl border border-border">
            <Star size={14} className="text-yellow-500 shrink-0" />
            <p className="text-xs text-stone-400">후렴구 강화 <span className="text-yellow-400 font-medium">ON (고정)</span> — 코러스 훅 5~8자, 최소 2회 반복, 에너지 2배</p>
          </div>
        </div>
      </div>

      {/* Section 4: Theme */}
      <div className="bg-card border border-border rounded-2xl p-5">
        <h3 className="text-sm font-semibold text-stone-300 mb-3">스토리 / 테마</h3>
        <textarea
          value={cfg.theme || ''}
          onChange={(e) => setLyricsConfig({ theme: e.target.value })}
          placeholder="어떤 이야기를 담고 싶나요? 자유롭게 적어주세요..."
          rows={3}
          className="w-full bg-elevated border border-border rounded-xl px-3 py-2.5 text-sm text-stone-300 placeholder-stone-500 focus:outline-none focus:border-orange-500 transition-colors resize-none"
        />
        <div className="flex gap-2 mt-2 flex-wrap">
          {EXAMPLE_THEMES.map((t) => (
            <button key={t} onClick={() => setLyricsConfig({ theme: t })}
              className="px-2.5 py-1 rounded-full border border-border text-xs text-stone-500 hover:text-stone-300 hover:border-stone-500 transition-all">
              {t}
            </button>
          ))}
        </div>
      </div>

      {/* Generate Button */}
      <button
        onClick={handleGenerate}
        disabled={loading}
        className="w-full py-4 rounded-2xl btn-primary text-white font-semibold text-base flex items-center justify-center gap-2"
      >
        {loading ? (
          <>
            <div className="flex gap-1">
              {[0,1,2,3,4].map(i => <span key={i} className="wave-bar h-5" style={{ animationDelay: `${i*0.15}s` }} />)}
            </div>
            AI 가사 생성 중...
          </>
        ) : (
          <><Sparkles size={18} />✨ AI 가사 생성</>
        )}
      </button>

      {/* Lyrics Result */}
      {lyrics?.lyrics && (
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="space-y-3">
          <h3 className="text-sm font-semibold text-stone-300">생성된 가사</h3>
          {lyrics.lyrics.map((item, i) => (
            <div key={i} className={`relative rounded-xl border-2 p-4 transition-all ${item.is_chorus ? 'border-yellow-500/60 bg-yellow-500/5 chorus-glow' : 'border-border bg-card'}`}>
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-center gap-2 mb-1">
                  {item.is_chorus && <span className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-yellow-500/20 text-yellow-400 text-xs font-bold"><Star size={10} fill="currentColor" />CHORUS</span>}
                  <span className="text-xs text-stone-500">{item.section}</span>
                  <span className="text-xs text-stone-500">{item.time_start}s–{item.time_end}s</span>
                </div>
                <button onClick={() => startEdit(i, item.text)} className="text-stone-500 hover:text-stone-400 shrink-0">
                  <Edit2 size={12} />
                </button>
              </div>
              {editingIndex === i ? (
                <div className="space-y-2">
                  <textarea
                    value={editText}
                    onChange={(e) => setEditText(e.target.value)}
                    rows={2}
                    className="w-full bg-elevated border border-orange-500 rounded-lg px-2.5 py-1.5 text-sm text-stone-300 focus:outline-none resize-none"
                  />
                  <button onClick={() => saveEdit(i)} className="flex items-center gap-1 px-3 py-1 rounded-lg bg-orange-500/20 text-orange-400 text-xs">
                    <Check size={10} />저장
                  </button>
                </div>
              ) : (
                <p className="text-stone-300 text-sm whitespace-pre-line">{item.text}</p>
              )}
              {item.hook_line && <p className="mt-1 text-yellow-400 text-xs font-medium">훅: "{item.hook_line}"</p>}
            </div>
          ))}

          <div className="flex gap-3 pt-2">
            <button onClick={handleRegenerate} disabled={loading}
              className="flex-1 py-3 rounded-xl border border-border text-stone-400 hover:text-stone-300 hover:border-stone-500 flex items-center justify-center gap-2 text-sm transition-all">
              <RefreshCw size={14} />재생성
            </button>
            <button onClick={handleConfirm}
              className="flex-1 py-3 rounded-xl btn-primary text-white font-semibold text-sm flex items-center justify-center gap-2">
              확정 → 스토리 생성
              <ChevronRight size={16} />
            </button>
          </div>
        </motion.div>
      )}
    </div>
  )
}
