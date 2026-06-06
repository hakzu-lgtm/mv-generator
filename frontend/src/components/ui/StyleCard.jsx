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
      {STYLE_BADGE[style] && (
        <div className="mt-1 text-[10px] px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 inline-block">
          {STYLE_BADGE[style]}
        </div>
      )}
    </motion.button>
  )
}
