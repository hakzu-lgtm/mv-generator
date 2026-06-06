import { Check } from 'lucide-react'
import { motion } from 'framer-motion'

const STYLE_ICONS = {
  '한국웹툰시트': '📋', '시네마틱판타지': '🎬',
  '지브리': '🌿', '픽사3D': '🏆', '클레이': '🟤', '2D일러스트': '✏️',
  '수채화': '🎨', '일본애니': '⛩️', '시네마틱실사': '📽️', '빈티지필름': '📷',
  '네온사이버펑크': '🌃', '판타지': '🔮', '미니멀모노톤': '⬜', '마블코믹스': '💥',
  '오일페인팅': '🖌️', '픽셀아트': '👾', '수묵화': '🖊️',
}

const STYLE_BADGE = {
  '한국웹툰시트': '레퍼런스',
  '시네마틱판타지': '레퍼런스',
}

const STYLE_DESC = {
  '한국웹툰시트': '밝고 산뜻한 Pixiv풍',
  '시네마틱판타지': 'AAA게임+K드라마 사실풍',
  '지브리': '지브리 수채화 따뜻함',
  '픽사3D': '픽사 CGI 시네마틱',
  '클레이': '클레이 스탑모션',
  '2D일러스트': '깔끔한 볼드 일러스트',
  '수채화': '물감 번짐 몽환풍',
  '일본애니': '고품질 일본 애니',
  '시네마틱실사': '시네마틱 사진 실사',
  '빈티지필름': '아날로그 필름 감성',
  '네온사이버펑크': '네온 사이버펑크 도시',
  '판타지': '에픽 판타지 마법',
  '미니멀모노톤': '미니멀 흑백 그래픽',
  '마블코믹스': '마블 코믹 히어로',
  '오일페인팅': '고전 유화 명화풍',
  '픽셀아트': '레트로 픽셀 게임',
  '수묵화': '동양 수묵 선화풍',
}

export default function StyleCard({ style, selected, onClick }) {
  return (
    <motion.button
      whileHover={{ scale: 1.03 }}
      whileTap={{ scale: 0.97 }}
      onClick={onClick}
      className={`relative p-3 rounded-xl border-2 text-left transition-all ${
        selected
          ? 'border-stone-400/70 bg-stone-600/25 text-stone-100'
          : 'border-border bg-elevated text-stone-400 hover:border-stone-500 hover:text-stone-300'
      }`}
    >
      {selected && (
        <div className="absolute top-2 right-2 w-4 h-4 bg-stone-400 rounded-full flex items-center justify-center">
          <Check size={10} className="text-white" />
        </div>
      )}
      <div className="text-2xl mb-1">{STYLE_ICONS[style] || '🎨'}</div>
      <div className="text-xs font-medium">{style}</div>
      {STYLE_DESC[style] && (
        <div className="mt-0.5 text-[10px] text-stone-500 leading-tight">{STYLE_DESC[style]}</div>
      )}
      {STYLE_BADGE[style] && (
        <div className="mt-1 text-[10px] px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 inline-block">
          {STYLE_BADGE[style]}
        </div>
      )}
    </motion.button>
  )
}
