import { useState } from 'react'
import Header from './Header'
import Sidebar from './Sidebar'
import Step1_Lyrics from '../steps/Step1_Lyrics'
import Step2_Story from '../steps/Step2_Story'
import Step3_Music from '../steps/Step2_Music'
import Step4_Images from '../steps/Step3_Images'
import Step5_Video from '../steps/Step4_Video'
import Step6_Final from '../steps/Step5_Final'
import ApiSetup from '../setup/ApiSetup'
import useProjectStore from '../../store/projectStore'
import { AnimatePresence, motion } from 'framer-motion'

const STEP_COMPONENTS = {
  1: Step1_Lyrics,
  2: Step2_Story,
  3: Step3_Music,
  4: Step4_Images,
  5: Step5_Video,
  6: Step6_Final,
}

export default function MainApp() {
  const { currentStep, setApiKeys, clearApiKeys } = useProjectStore()
  const [showSettings, setShowSettings] = useState(false)

  const StepComponent = STEP_COMPONENTS[currentStep] || Step1_Lyrics

  if (showSettings) {
    return <ApiSetup onComplete={() => setShowSettings(false)} />
  }

  return (
    <div
      className="flex flex-col h-screen overflow-hidden"
      style={{
        background:
          'radial-gradient(ellipse 90% 40% at 50% -5%, rgba(249,115,22,0.09), transparent), #2C1A0A',
      }}
    >
      <Header onSettings={() => setShowSettings(true)} />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <main className="flex-1 overflow-y-auto p-6">
          <AnimatePresence mode="wait">
            <motion.div
              key={currentStep}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -12 }}
              transition={{ duration: 0.25 }}
            >
              <StepComponent />
            </motion.div>
          </AnimatePresence>
        </main>
      </div>
    </div>
  )
}
