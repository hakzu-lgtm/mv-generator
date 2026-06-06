import { CheckCircle, Circle, Lock, Music, Image, Film, Layers, FileText, BookOpen } from 'lucide-react'
import { motion } from 'framer-motion'
import useProjectStore from '../../store/projectStore'
import CostTracker from '../ui/CostTracker'

const STEPS = [
  { id: 1, label: '가사',   sublabel: 'Gemini · 무료',   icon: FileText },
  { id: 2, label: '스토리', sublabel: 'Gemini · 무료',   icon: BookOpen },
  { id: 3, label: '음악',   sublabel: 'Lyria 3 Pro',     icon: Music    },
  { id: 4, label: '이미지', sublabel: 'Nano Banana 2',   icon: Image    },
  { id: 5, label: '영상',   sublabel: 'Veo 3.1 Fast',    icon: Film     },
  { id: 6, label: '완성',   sublabel: 'FFmpeg · 무료',   icon: Layers   },
]
const NUMS = '①②③④⑤⑥'

export default function Sidebar() {
  const { currentStep, completedSteps, setStep } = useProjectStore()

  const canGo = (stepId) =>
    stepId === 1 || completedSteps.includes(stepId - 1) || completedSteps.includes(stepId)

  return (
    <aside className="w-[220px] bg-card border-r border-border flex flex-col shrink-0"
      style={{ boxShadow: '1px 0 0 rgba(249,115,22,0.06)' }}
    >
      <div className="p-4 space-y-0.5 flex-1">
        <p className="text-[10px] text-stone-600 font-semibold uppercase tracking-widest mb-3 px-2">
          제작 단계
        </p>

        {STEPS.map((step) => {
          const isDone    = completedSteps.includes(step.id)
          const isCurrent = currentStep === step.id
          const isLocked  = !canGo(step.id)
          const Icon      = step.icon

          return (
            <motion.button
              key={step.id}
              whileHover={!isLocked ? { x: 3 } : {}}
              onClick={() => !isLocked && setStep(step.id)}
              disabled={isLocked}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-left transition-all ${
                isCurrent
                  ? 'bg-stone-600/30 border border-stone-500/30 text-stone-100'
                  : isDone
                  ? 'text-amber-400 hover:bg-stone-700/30'
                  : isLocked
                  ? 'text-stone-700 cursor-not-allowed'
                  : 'text-stone-400 hover:bg-elevated hover:text-stone-200'
              }`}
            >
              <div className="shrink-0">
                {isDone ? (
                  <CheckCircle size={16} className="text-amber-400" />
                ) : isCurrent ? (
                  <div className="w-4 h-4 rounded-full border-2 border-orange-400 flex items-center justify-center shrink-0">
                    <div className="w-1.5 h-1.5 rounded-full bg-orange-400 animate-pulse" />
                  </div>
                ) : isLocked ? (
                  <Lock size={16} className="text-stone-700" />
                ) : (
                  <Circle size={16} className="text-stone-600" />
                )}
              </div>
              <div className="min-w-0">
                <div className="text-sm font-medium">
                  <span className="text-stone-600 mr-1">{NUMS[step.id - 1]}</span>
                  {step.label}
                </div>
                <div className="text-xs text-stone-600 truncate">{step.sublabel}</div>
              </div>
            </motion.button>
          )
        })}
      </div>

      <div className="p-4 border-t border-border">
        <CostTracker />
      </div>
    </aside>
  )
}
