import { DollarSign, AlertTriangle, TrendingUp } from 'lucide-react'
import { useCostGuard } from '../../hooks/useCostGuard'

export default function CostTracker({ compact = false }) {
  const { sessionCost, remaining, percentage, isOverLimit, limit } = useCostGuard()

  const barColor = percentage >= 90 ? 'bg-red-500' : percentage >= 70 ? 'bg-yellow-500' : 'bg-orange-500'
  const textColor = percentage >= 90 ? 'text-red-400' : percentage >= 70 ? 'text-yellow-400' : 'text-orange-400'

  if (compact) {
    return (
      <div className={`flex items-center gap-2 text-sm ${textColor}`}>
        {isOverLimit ? <AlertTriangle size={14} /> : <DollarSign size={14} />}
        <span className="font-mono font-semibold">${sessionCost.toFixed(2)}</span>
        <span className="text-stone-500">/ ${limit}</span>
      </div>
    )
  }

  return (
    <div className="bg-card border border-border rounded-xl p-4 space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-stone-300">
          <TrendingUp size={16} className={textColor} />
          <span className="text-sm font-medium">세션 사용액</span>
        </div>
        <div className={`text-lg font-bold font-mono ${textColor}`}>
          ${sessionCost.toFixed(2)}
          <span className="text-stone-500 text-sm font-normal"> / ${limit}</span>
        </div>
      </div>

      <div className="relative h-2 bg-stone-800 rounded-full overflow-hidden">
        <div
          className={`absolute inset-y-0 left-0 rounded-full transition-all duration-500 ${barColor}`}
          style={{ width: `${percentage}%` }}
        />
      </div>

      <div className="flex justify-between text-xs text-stone-500">
        <span>남은 안전 크레딧: <span className="text-stone-300">${remaining.toFixed(2)}</span></span>
        <span>{percentage.toFixed(0)}% 사용</span>
      </div>

      {isOverLimit && (
        <div className="flex items-center gap-2 bg-red-500/10 border border-red-500/30 rounded-lg p-2 text-red-400 text-xs">
          <AlertTriangle size={12} />
          안전 한도 도달. 더 진행하면 크레딧 소진 위험
        </div>
      )}
    </div>
  )
}
