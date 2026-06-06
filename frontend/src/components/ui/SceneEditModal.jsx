import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Edit3 } from 'lucide-react'

const QUICK_FIXES = ['더 밝게', '더 어둡게', '클로즈업', '와이드샷', '역동적으로', '차분하게']

export default function SceneEditModal({ isOpen, onClose, onConfirm, sceneId }) {
  const [instruction, setInstruction] = useState('')

  if (!isOpen) return null

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="absolute inset-0 bg-black/70 backdrop-blur-sm"
          onClick={onClose}
        />
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="relative bg-elevated border border-border rounded-2xl p-6 w-full max-w-md mx-4"
        >
          <button onClick={onClose} className="absolute top-4 right-4 text-stone-500">
            <X size={16} />
          </button>

          <div className="flex items-center gap-2 mb-4">
            <Edit3 size={18} className="text-orange-400" />
            <h3 className="font-semibold text-stone-200">씬 {sceneId + 1} 수정</h3>
          </div>

          <div className="flex gap-2 flex-wrap mb-3">
            {QUICK_FIXES.map((q) => (
              <button key={q} onClick={() => setInstruction(q)}
                className="px-2.5 py-1 rounded-full bg-card border border-border text-xs text-stone-400 hover:text-stone-300 transition-all">
                {q}
              </button>
            ))}
          </div>

          <textarea
            value={instruction}
            onChange={(e) => setInstruction(e.target.value)}
            placeholder="수정 지시사항을 입력하세요..."
            rows={3}
            className="w-full bg-primary border border-border rounded-xl px-3 py-2.5 text-sm text-stone-300 placeholder-stone-500 focus:outline-none focus:border-orange-500 resize-none"
          />

          <div className="flex gap-3 mt-4">
            <button onClick={onClose} className="flex-1 py-2.5 rounded-xl border border-border text-stone-400 text-sm">취소</button>
            <button onClick={() => { onConfirm(instruction); onClose() }}
              className="flex-1 py-2.5 rounded-xl btn-primary text-white font-medium text-sm">재생성</button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  )
}
