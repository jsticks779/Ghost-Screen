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
            Secure your desktop with <span className="text-accent">Ghost Screen</span>.
          </h1>
          <p className="text-base sm:text-lg text-muted-foreground max-w-xl mx-auto mb-10 leading-relaxed">
            Use any shortcut you like to lock and unlock your screen any time.
            Use any wallpaper, video or image you like.
            After installation, Ghost Screen uses <kbd className="px-1.5 py-0.5 text-xs font-mono bg-muted border border-border rounded">Ctrl</kbd>+<kbd className="px-1.5 py-0.5 text-xs font-mono bg-muted border border-border rounded">3</kbd> by default — you can change it to whatever you want.
            Works on Linux &amp; Windows.
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
