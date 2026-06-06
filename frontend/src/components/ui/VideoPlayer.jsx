import { useRef, useState } from 'react'
import { Play, Pause, Download, Film } from 'lucide-react'

export default function VideoPlayer({ src, title = '뮤직비디오', fileSize, clipCount }) {
  const videoRef = useRef(null)
  const [playing, setPlaying] = useState(false)

  const toggle = () => {
    const v = videoRef.current
    if (!v) return
    if (playing) { v.pause(); setPlaying(false) }
    else { v.play(); setPlaying(true) }
  }

  return (
    <div className="space-y-3">
      <div className="relative bg-black rounded-2xl overflow-hidden aspect-video border border-border">
        {src ? (
          <video
            ref={videoRef}
            src={src}
            className="w-full h-full object-contain"
            onEnded={() => setPlaying(false)}
            controls
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <div className="text-center">
              <Film size={48} className="text-stone-600 mx-auto mb-2" />
              <p className="text-stone-500 text-sm">영상 미리보기</p>
            </div>
          </div>
        )}
      </div>

      {src && (
        <div className="flex items-center justify-between bg-elevated border border-border rounded-xl px-4 py-3">
          <div className="text-sm text-stone-400 space-y-0.5">
            <p className="text-stone-300 font-medium">{title}</p>
            <p className="text-xs">{fileSize && `${fileSize}MB`} {clipCount && `· ${clipCount}씬`}</p>
          </div>
          <a
            href={src}
            download
            className="flex items-center gap-2 px-4 py-2 rounded-xl btn-primary text-white text-sm"
          >
            <Download size={14} />
            다운로드
          </a>
        </div>
      )}
    </div>
  )
}
