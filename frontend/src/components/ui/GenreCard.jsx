import { Check } from 'lucide-react'
import { motion } from 'framer-motion'

const GENRE_ICONS = {
  '트롯트': '🎺', 'K-POP': '🎤', '댄스': '💃', 'K-힙합': '🎧',
  '발라드': '💙', '인디팝': '🎸', '시티팝': '🌆', '신스팝': '🎹',
  '시네마틱': '🎬', '어쿠스틱': '🪕', '재즈': '🎷', '록': '🤘',
}

export default function GenreCard({ genre, selected, onClick }) {
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
      <div className="text-2xl mb-1">{GENRE_ICONS[genre] || '🎵'}</div>
      <div className="text-xs font-medium">{genre}</div>
    </motion.button>
  )
}
