import { Settings, HelpCircle, AlertTriangle, Flame } from 'lucide-react'
import { useCostGuard } from '../../hooks/useCostGuard'
import CostTracker from '../ui/CostTracker'

export default function Header({ onSettings }) {
  const { isOverLimit } = useCostGuard()

  return (
    <header className="h-14 bg-card border-b border-border flex items-center px-5 gap-4 shrink-0 z-10"
      style={{ boxShadow: '0 1px 0 rgba(249,115,22,0.08)' }}
    >
      <div className="flex items-center gap-2.5">
        <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-orange-500 to-amber-600 flex items-center justify-center shadow-lg">
          <Flame size={14} className="text-white" />
        </div>
        <span className="font-bold text-[#FEF3E2] tracking-wide text-sm">MV Generator</span>
        <span className="text-[10px] px-1.5 py-0.5 rounded bg-orange-500/15 text-orange-400 border border-orange-500/20 font-medium">
          PRO
        </span>
      </div>

      {isOverLimit && (
        <div className="flex items-center gap-1.5 bg-red-500/10 border border-red-500/30 rounded-lg px-2.5 py-1 text-red-400 text-xs">
          <AlertTriangle size={12} />
          안전 한도 도달
        </div>
      )}

      <div className="ml-auto flex items-center gap-3">
        <CostTracker compact />
        <div className="h-4 w-px bg-border" />
        <button
          onClick={onSettings}
          className="text-stone-500 hover:text-orange-400 transition-colors"
          title="API 설정"
        >
          <Settings size={18} />
        </button>
        <a
          href="https://github.com"
          target="_blank"
          rel="noopener noreferrer"
          className="text-stone-500 hover:text-orange-400 transition-colors"
        >
          <HelpCircle size={18} />
        </a>
      </div>
    </header>
  )
}
