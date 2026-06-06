import { create } from 'zustand'
import { persist } from 'zustand/middleware'

const generateId = () => Math.random().toString(36).slice(2, 10)

const useProjectStore = create(
  persist(
    (set, get) => ({
      // API Keys
      apiKeys: null,
      setApiKeys: (keys) => set({ apiKeys: keys }),
      clearApiKeys: () => set({ apiKeys: null }),

      // Project
      projectId: generateId(),
      resetProject: () => set({ projectId: generateId(), currentStep: 1, completedSteps: [], lyrics: null, story: null, music: null, images: null, video: null, clips: [], scenes: [], character: null, charBasePrompt: '' }),

      // Steps
      currentStep: 1,
      setStep: (step) => set({ currentStep: step }),
      completedSteps: [],
      markStepComplete: (step) => set((s) => ({
        completedSteps: [...new Set([...s.completedSteps, step])],
      })),

      // Lyrics (Step 1)
      lyrics: null,

      // Story (Step 2)
      story: null,
      setStory: (data) => set({ story: data }),
      lyricsConfig: {
        genre: ['K-POP'],
        vocalist: { gender: '여성', age: '20대', style: '청아한' },
        music: { bpm: 120, instruments: ['피아노', '신시사이저'] },
        theme: '',
      },
      setLyricsConfig: (cfg) => set((s) => ({ lyricsConfig: { ...s.lyricsConfig, ...cfg } })),
      setLyrics: (data) => set({ lyrics: data }),

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
