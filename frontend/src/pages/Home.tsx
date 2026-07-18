import { useRef, useEffect } from 'react'
import Header from '@/components/Header'
import InstallSection from '@/components/InstallSection'
import Features from '@/components/Features'
import FAQ from '@/components/FAQ'
import Footer from '@/components/Footer'

export default function Home() {
  const videoRef = useRef<HTMLVideoElement>(null)

  useEffect(() => {
    if (videoRef.current) videoRef.current.playbackRate = 1.5
  }, [])

  return (
    <>
      <Header />

      <section className="pt-24 pb-12 px-6 text-center relative">
        <img
          src="/shield.png"
          alt=""
          className="absolute right-4 sm:right-[10%] top-14 sm:top-8 w-10 sm:w-24 opacity-80 pointer-events-none select-none animate-shield-float"
        />
        <div className="max-w-3xl mx-auto">
          <h1 className="text-5xl sm:text-6xl font-bold tracking-tight leading-tight mb-4">
            Secure your desktop with <span className="text-accent">Ghost Screen<span className="animate-blink text-accent ml-0.5 font-light">|</span></span>
          </h1>
          <p className="text-base sm:text-lg text-muted-foreground max-w-xl mx-auto mb-10 leading-relaxed">
            Use any shortcut you like to lock and unlock your screen any time.
            Use any wallpaper, video or image you like.
            After installation, Ghost Screen uses <kbd className="px-1.5 py-0.5 text-xs font-mono bg-muted border border-border rounded">Ctrl</kbd>+<kbd className="px-1.5 py-0.5 text-xs font-mono bg-muted border border-border rounded">3</kbd> by default — you can change it to whatever you want.
            Works on Linux &amp; Windows.
          </p>

          <InstallSection />

          <div className="max-w-lg mx-auto bg-card border border-border rounded-lg overflow-hidden">
            <div className="video-zoom relative" style={{ paddingBottom: '47.3%' }}>
              <video
                ref={videoRef}
                autoPlay
                muted
                loop
                playsInline
                className="absolute inset-0 w-full h-full object-contain"
              >
                <source src="/ghost-screen.webm" type="video/webm" />
                <source src="/ghost-screen.mp4" type="video/mp4" />
                Your browser does not support the video tag.
              </video>
            </div>
          </div>
        </div>
      </section>

      <section className="py-16 px-6 border-t border-border">
        <div className="max-w-2xl mx-auto text-center">
          <h2 className="text-2xl font-bold mb-3">Built for privacy first</h2>
          <p className="text-sm text-muted-foreground leading-relaxed">
            Ghost Screen runs entirely offline on your machine. No data, no keystrokes, no screen content
            is ever sent anywhere. Everything stays local — because your desktop is yours alone.
          </p>
        </div>
      </section>

      <Features />
      <FAQ />
      <Footer />
    </>
  )
}
