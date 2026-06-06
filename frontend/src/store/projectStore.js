import { create } from 'zustand'
import { persist } from 'zustand/middleware'

const generateProjectId = () => {
  const now = new Date()
  const pad = (n, len = 2) => String(n).padStart(len, '0')
  const date = `${now.getFullYear()}${pad(now.getMonth() + 1)}${pad(now.getDate())}`
  const time = `${pad(now.getHours())}${pad(now.getMinutes())}${pad(now.getSeconds())}`
  const rand = Math.random().toString(36).slice(2, 6)
  return `proj_${date}_${time}_${rand}`
}

const EMPTY_PROJECT_STATE = {
  currentStep: 1,
  completedSteps: [],
  lyricsConfig: {
    genre: ['K-POP'],
    vocalist: { gender: '여성', age: '20대', style: '청아한' },
    music: { bpm: 120, instruments: ['피아노', '신시사이저'] },
    theme: '',
  },
  lyrics: null,
  story: null,
  music: null,
  selectedStyle: '지브리',
  character: null,
  charBasePrompt: '',
  scenes: [],
  images: null,
  video: null,
  clips: [],
  sessionCost: 0,
  sseLog: [],
}

const useProjectStore = create(
  persist(
    (set, get) => ({
      // API Keys
      apiKeys: null,
      setApiKeys: (keys) => set({ apiKeys: keys }),
      clearApiKeys: () => set({ apiKeys: null }),

      // Project
      projectId: generateProjectId(),
      newProject: () => set({ projectId: generateProjectId(), ...EMPTY_PROJECT_STATE }),
      resetProject: () => set({ projectId: generateProjectId(), ...EMPTY_PROJECT_STATE }),

      // Steps
      currentStep: 1,
      setStep: (step) => set({ currentStep: step }),
      completedSteps: [],
      markStepComplete: (step) => set((s) => ({
        completedSteps: [...new Set([...s.completedSteps, step])],
      })),

      // Lyrics (Step 1)
      lyrics: null,
      lyricsConfig: {
        genre: ['K-POP'],
        vocalist: { gender: '여성', age: '20대', style: '청아한' },
        music: { bpm: 120, instruments: ['피아노', '신시사이저'] },
        theme: '',
      },
      setLyricsConfig: (cfg) => set((s) => ({ lyricsConfig: { ...s.lyricsConfig, ...cfg } })),
      setLyrics: (data) => set({ lyrics: data }),

      // Story (Step 2)
      story: null,
      setStory: (data) => set({ story: data }),

      // Music (Step 2)
      music: null,
      setMusic: (data) => set({ music: data }),

      // Images (Step 3)
      selectedStyle: '지브리',
      setSelectedStyle: (style) => set({ selectedStyle: style }),
      character: null,
      setCharacter: (char) => set({ character: char }),
      charBasePrompt: '',
      setCharBasePrompt: (p) => set({ charBasePrompt: p }),
      scenes: [],
      setScenes: (scenes) => set({ scenes }),
      images: null,
      setImages: (data) => set({ images: data }),

      // Video (Step 4)
      video: null,
      setVideo: (data) => set({ video: data }),
      clips: [],
      setClips: (clips) => set({ clips }),

      // Cost tracking
      sessionCost: 0,
      setSessionCost: (cost) => set({ sessionCost: cost }),

      // SSE log
      sseLog: [],
      addSseLog: (msg) => set((s) => ({
        sseLog: [...s.sseLog.slice(-50), { msg, time: Date.now() }],
      })),
      clearSseLog: () => set({ sseLog: [] }),
    }),
    {
      name: 'mv-generator-project',
      partialize: (s) => ({
        apiKeys: s.apiKeys,
        projectId: s.projectId,
        currentStep: s.currentStep,
        completedSteps: s.completedSteps,
        lyricsConfig: s.lyricsConfig,
        lyrics: s.lyrics,
        story: s.story,
        music: s.music,
        selectedStyle: s.selectedStyle,
        character: s.character,
        charBasePrompt: s.charBasePrompt,
        scenes: s.scenes,
        sessionCost: s.sessionCost,
      }),
    }
  )
)

export default useProjectStore
