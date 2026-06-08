import { useState, useRef, useEffect } from 'react'
import { Play, Pause, Volume2, Music } from 'lucide-react'

export default function AudioPlayer({ src, title = '음악', duration = 0, bpm = 120 }) {
  const audioRef = useRef(null)
  const [playing, setPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [audioDuration, setAudioDuration] = useState(duration)
  const [volume, setVolume] = useState(0.8)
  const [hasError, setHasError] = useState(false)

  useEffect(() => {
    const audio = audioRef.current
    if (!audio) return
    // src가 바뀌면 에러 상태 초기화하고 다시 로드
    setHasError(false)
    setPlaying(false)
    setCurrentTime(0)
    audio.load()
    const onTime = () => setCurrentTime(audio.currentTime)
    const onMeta = () => setAudioDuration(audio.duration || duration)
    const onEnd = () => setPlaying(false)
    const onErr = () => setHasError(true)
    audio.addEventListener('timeupdate', onTime)
    audio.addEventListener('loadedmetadata', onMeta)
    audio.addEventListener('ended', onEnd)
    audio.addEventListener('error', onErr)
    return () => {
      audio.removeEventListener('timeupdate', onTime)
      audio.removeEventListener('loadedmetadata', onMeta)
      audio.removeEventListener('ended', onEnd)
      audio.removeEventListener('error', onErr)
    }
  }, [src, duration])

  const toggle = async () => {
    const audio = audioRef.current
    if (!audio) return
    if (playing) {
      audio.pause()
      setPlaying(false)
    } else {
      // 에러 상태면 재로드 후 재시도
      if (hasError) {
        setHasError(false)
        audio.load()
        await new Promise((r) => setTimeout(r, 300))
      }
      try {
        await audio.play()
        setPlaying(true)
      } catch (e) {
        console.warn('[AudioPlayer] play() failed:', e)
        setHasError(true)
      }
    }
  }

  const seek = (e) => {
    const audio = audioRef.current
    if (!audio || !audioDuration) return
    const rect = e.currentTarget.getBoundingClientRect()
    const ratio = (e.clientX - rect.left) / rect.width
    audio.currentTime = ratio * audioDuration
  }

  const fmt = (s) => {
    if (!s || isNaN(s)) return '0:00'
    const m = Math.floor(s / 60)
    const sec = Math.floor(s % 60)
    return `${m}:${sec.toString().padStart(2, '0')}`
  }

  const progress = audioDuration > 0 ? (currentTime / audioDuration) * 100 : 0

  return (
    <div className="bg-elevated border border-border rounded-2xl p-4 space-y-3">
      <audio ref={audioRef} src={src} preload="metadata" />

      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-orange-500/20 flex items-center justify-center shrink-0">
          {playing ? (
            <div className="flex gap-0.5 items-center">
              {[0, 1, 2, 3].map((i) => (
                <span key={i} className="wave-bar h-4" style={{ animationDelay: `${i * 0.15}s` }} />
              ))}
            </div>
          ) : (
            <Music size={18} className="text-orange-400" />
          )}
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-stone-300 font-medium text-sm truncate">{title}</p>
          <p className="text-stone-500 text-xs">{bpm} BPM · {fmt(audioDuration)}</p>
        </div>
        <button
          onClick={toggle}
          className="w-9 h-9 rounded-full btn-primary flex items-center justify-center shrink-0"
        >
          {playing ? <Pause size={14} className="text-white" /> : <Play size={14} className="text-white ml-0.5" />}
        </button>
      </div>

      <div
        className="relative h-1.5 bg-stone-800 rounded-full cursor-pointer overflow-hidden"
        onClick={seek}
      >
        <div
          className="absolute inset-y-0 left-0 bg-orange-500 rounded-full transition-all"
          style={{ width: `${progress}%` }}
        />
      </div>

      <div className="flex justify-between text-xs text-stone-500">
        <span>{fmt(currentTime)}</span>
        <span>{fmt(audioDuration)}</span>
      </div>

      {hasError && (
        <p className="text-xs text-stone-500 text-center">
          오디오 미리듣기를 사용할 수 없습니다 (파일이 생성된 후 재생 가능)
        </p>
      )}
    </div>
  )
}
