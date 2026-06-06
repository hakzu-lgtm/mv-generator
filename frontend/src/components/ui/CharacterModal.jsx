import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, User, Sparkles } from 'lucide-react'

const FIELDS = [
  { key: 'name', label: '이름', placeholder: '예: 지민, 하늘, 태양' },
  { key: 'age', label: '나이/나이대', placeholder: '예: 20대 초반' },
  { key: 'gender', label: '성별', placeholder: '예: 여성, 남성' },
  { key: 'hair', label: '헤어스타일', placeholder: '예: 긴 검은 생머리' },
  { key: 'outfit', label: '의상', placeholder: '예: 흰 블라우스, 청바지' },
  { key: 'feature', label: '특징', placeholder: '예: 큰 눈, 밝은 미소' },
  { key: 'mood', label: '분위기', placeholder: '예: 청순한, 강인한, 몽환적' },
]

export default function CharacterModal({ isOpen, onClose, onConfirm, initialData = {} }) {
  const [form, setForm] = useState({
    name: '',
    age: '20대',
    gender: '여성',
    hair: '검은 긴 머리',
    outfit: '캐주얼',
    feature: '',
    mood: '청순한',
    ...initialData,
  })

  if (!isOpen) return null

  const handleConfirm = () => {
    onConfirm(form)
    onClose()
  }

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="absolute inset-0 bg-black/70 backdrop-blur-sm"
          onClick={onClose}
        />
        <motion.div
          initial={{ opacity: 0, scale: 0.9, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.9 }}
          className="relative bg-elevated border border-border rounded-2xl p-6 w-full max-w-lg mx-4 shadow-2xl max-h-[90vh] overflow-y-auto"
        >
          <button onClick={onClose} className="absolute top-4 right-4 text-stone-500 hover:text-stone-300">
            <X size={18} />
          </button>

          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-xl bg-amber-500/20 flex items-center justify-center">
              <User size={20} className="text-amber-400" />
            </div>
            <div>
              <h3 className="font-semibold text-stone-200">캐릭터 외모 설정</h3>
              <p className="text-xs text-stone-500">이미지 일관성을 위해 상세히 입력하세요</p>
            </div>
          </div>

          <div className="space-y-3">
            {FIELDS.map(({ key, label, placeholder }) => (
              <div key={key}>
                <label className="block text-xs text-stone-500 mb-1">{label}</label>
                <input
                  value={form[key] || ''}
                  onChange={(e) => setForm((f) => ({ ...f, [key]: e.target.value }))}
                  placeholder={placeholder}
                  className="w-full bg-primary border border-border rounded-xl px-3 py-2 text-sm text-stone-300 placeholder-stone-500 focus:outline-none focus:border-orange-500 transition-colors"
                />
              </div>
            ))}
          </div>

          <div className="flex gap-3 mt-6">
            <button onClick={onClose} className="flex-1 py-2.5 rounded-xl border border-border text-stone-400 text-sm hover:text-stone-300 transition-colors">
              취소
            </button>
            <button onClick={handleConfirm} className="flex-1 py-2.5 rounded-xl btn-primary text-white font-medium text-sm flex items-center justify-center gap-2">
              <Sparkles size={14} />
              확정
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  )
}
