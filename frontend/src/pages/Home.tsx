import Header from '@/components/Header'
import InstallSection from '@/components/InstallSection'
import Features from '@/components/Features'
import Backends from '@/components/Backends'
import Stats from '@/components/Stats'
import FAQ from '@/components/FAQ'
import Footer from '@/components/Footer'

export default function Home() {
  return (
    <>
      <Header />

      <section className="pt-24 pb-12 px-6 text-center">
        <div className="max-w-3xl mx-auto">
          <h1 className="text-5xl sm:text-6xl font-bold tracking-tight leading-tight mb-4">
            Animated tech <span className="gradient-text">ghost overlay</span>
          </h1>
          <p className="text-lg text-muted-foreground max-w-xl mx-auto mb-10 leading-relaxed">
            Full-screen cyberpunk holographic screensaver for Linux &amp; Windows.
            Toggle on/off with <kbd className="px-1.5 py-0.5 text-xs font-mono bg-muted border border-border rounded">Ctrl</kbd>+<kbd className="px-1.5 py-0.5 text-xs font-mono bg-muted border border-border rounded">3</kbd>.
          </p>

          <InstallSection />

          <div className="max-w-lg mx-auto bg-card border border-border rounded-lg overflow-hidden">
            <video
              src="/ghost-screen.mp4"
              autoPlay
              muted
              loop
              playsInline
              className="w-full aspect-video object-cover"
            >
              Your browser does not support the video tag.
            </video>
          </div>
        </div>
      </section>

      <Features />
      <Backends />
      <Stats />
      <FAQ />
      <Footer />
    </>
  )
}
