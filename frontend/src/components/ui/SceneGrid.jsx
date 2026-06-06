import { Star, RefreshCw, CheckCircle, Film, ShieldAlert } from 'lucide-react'
import { motion } from 'framer-motion'

export default function SceneGrid({ scenes = [], projectId, onRegenerate, type = 'image' }) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
      {scenes.map((scene, i) => (
        <motion.div
          key={scene.scene_id ?? i}
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.05 }}
          className={`relative rounded-xl overflow-hidden border-2 transition-all ${
            scene.safety_blocked
              ? 'border-red-500/60 bg-red-500/5'
              : scene.is_chorus
              ? 'border-yellow-500/60 chorus-glow'
              : 'border-border hover:border-orange-500/40'
          }`}
        >
          {scene.safety_blocked && (
            <div className="absolute top-2 left-2 z-10 flex items-center gap-1 bg-red-500/90 text-white text-xs font-bold px-2 py-0.5 rounded-full">
              <ShieldAlert size={10} />안전필터 차단
            </div>
          )}
          {scene.is_chorus && (
            <div className="absolute top-2 left-2 z-10 flex items-center gap-1 bg-yellow-500/90 text-black text-xs font-bold px-2 py-0.5 rounded-full">
              <Star size={10} fill="currentColor" />
              CHORUS
            </div>
          )}

          <div className="aspect-video bg-elevated">
            {scene.file ? (
              type === 'video' ? (
                <video
                  src={`http://localhost:8000/output/${projectId}/05_clips/${scene.file}`}
                  className="w-full h-full object-cover"
                  controls
                  preload="metadata"
                />
              ) : (
                <img
                  src={`/api/images/file/${scene.file}?pid=${projectId}&t=${Date.now()}`}
                  alt={`씬 ${i + 1}`}
                  className="w-full h-full object-cover"
                  onError={(e) => { e.target.style.display = 'none' }}
                />
              )
            ) : (
              <div className="w-full h-full flex items-center justify-center">
                <Film size={24} className="text-stone-600" />
              </div>
            )}
          </div>

          <div className="p-2 bg-card">
            <div className="flex items-center justify-between gap-1">
              <p className="text-xs text-stone-400 truncate">{scene.section || `씬 ${i + 1}`}</p>
              {scene.model && scene.model !== 'placeholder' && (
                <span className="text-xs px-1 py-0.5 rounded bg-stone-800 text-stone-500 shrink-0">
                  {(scene.model || '').includes('gemini') ? 'NB Pro' : 'Img3'}
                </span>
              )}
            </div>
            {onRegenerate && (
              <button
                onClick={() => onRegenerate(scene.scene_id ?? i)}
                className="mt-1 flex items-center gap-1 text-xs text-stone-500 hover:text-orange-400 transition-colors"
              >
                <RefreshCw size={10} />
                재생성
              </button>
            )}
          </div>
        </motion.div>
      ))}
    </div>
  )
}
