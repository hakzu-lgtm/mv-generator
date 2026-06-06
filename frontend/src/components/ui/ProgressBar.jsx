import { motion } from 'framer-motion'

export default function ProgressBar({ logs = [], running = false }) {
  return (
    <div className="bg-primary rounded-xl p-4 max-h-48 overflow-y-auto space-y-1">
      {logs.length === 0 && !running && (
        <p className="text-stone-500 text-sm text-center py-4">로그가 여기에 표시됩니다</p>
      )}
      {running && logs.length === 0 && (
        <div className="flex items-center gap-3 text-orange-400 text-sm">
          <div className="flex gap-1">
            {[0, 1, 2, 3, 4].map((i) => (
              <span key={i} className="wave-bar h-4" style={{ animationDelay: `${i * 0.15}s` }} />
            ))}
          </div>
          <span>시작 중...</span>
        </div>
      )}
      {logs.map((log, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0, x: -8 }}
          animate={{ opacity: 1, x: 0 }}
          className="sse-log-item flex items-start gap-2 text-sm"
        >
          <span className="text-stone-500 text-xs mt-0.5 shrink-0">
            {new Date(log.time).toLocaleTimeString('ko-KR', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' })}
          </span>
          <span className={
            log.type === 'error' ? 'text-red-400' :
            log.type === 'complete' ? 'text-green-400' :
            log.type === 'scene_done' ? 'text-orange-400' :
            'text-stone-300'
          }>
            {log.message || JSON.stringify(log)}
          </span>
        </motion.div>
      ))}
      {running && logs.length > 0 && (
        <div className="flex items-center gap-2 text-orange-400 text-xs pt-1">
          <div className="flex gap-0.5">
            {[0, 1, 2].map((i) => (
              <span key={i} className="wave-bar h-3" style={{ animationDelay: `${i * 0.2}s` }} />
            ))}
          </div>
          <span>처리 중...</span>
        </div>
      )}
    </div>
  )
}
