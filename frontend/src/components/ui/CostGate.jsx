import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { DollarSign, AlertTriangle, X, Check } from 'lucide-react'

export default function CostGate({ isOpen, onConfirm, onCancel, estimated, service, currentTotal, limit = 250 }) {
  const wouldTotal = (currentTotal || 0) + (estimated || 0)
  const isRisky = wouldTotal > limit * 0.9

  if (!isOpen) return null

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="absolute inset-0 bg-black/70 backdrop-blur-sm"
          onClick={onCancel}
        />
        <motion.div
          initial={{ opacity: 0, scale: 0.9, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.9 }}
          className="relative bg-elevated border border-border rounded-2xl p-6 w-full max-w-md mx-4 shadow-2xl"
        >
          <button onClick={onCancel} className="absolute top-4 right-4 text-stone-500 hover:text-stone-300 transition-colors">
            <X size={18} />
          </button>

          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-xl bg-orange-500/20 flex items-center justify-center">
              <DollarSign size={20} className="text-orange-400" />
            </div>
            <div>
              <h3 className="font-semibold text-stone-200">비용 확인</h3>
              <p className="text-xs text-stone-500">{service} 생성 전 확인</p>
            </div>
          </div>

          <div className="bg-primary rounded-xl p-4 space-y-2 mb-4">
            <div className="flex justify-between text-sm">
              <span className="text-stone-400">이번 작업 예상 비용</span>
              <span className="text-orange-400 font-mono font-semibold">${(estimated || 0).toFixed(2)}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-stone-400">현재 누적 사용액</span>
              <span className="text-stone-300 font-mono">${(currentTotal || 0).toFixed(2)}</span>
            </div>
            <div className="border-t border-border pt-2 flex justify-between text-sm">
              <span className="text-stone-300 font-medium">진행 후 합계</span>
              <span className={`font-mono font-bold ${isRisky ? 'text-yellow-400' : 'text-green-400'}`}>
                ${wouldTotal.toFixed(2)}
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-stone-500">안전 한도</span>
              <span className="text-stone-500 font-mono">${limit.toFixed(2)}</span>
            </div>
          </div>

          {isRisky && (
            <div className="flex items-center gap-2 bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-3 mb-4 text-yellow-400 text-xs">
              <AlertTriangle size={14} />
              안전 한도에 근접하고 있습니다. 신중히 진행하세요.
            </div>
          )}

          <div className="flex gap-3">
            <button
              onClick={onCancel}
              className="flex-1 py-2.5 rounded-xl border border-border text-stone-400 hover:text-stone-300 hover:border-stone-500 transition-colors text-sm"
            >
              취소
            </button>
            <button
              onClick={onConfirm}
              className="flex-1 py-2.5 rounded-xl btn-primary text-white font-medium text-sm flex items-center justify-center gap-2"
            >
              <Check size={16} />
              진행하기
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  )
}
