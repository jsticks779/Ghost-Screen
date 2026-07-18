import Header from './components/Header'
import InstallSection from './components/InstallSection'
import Features from './components/Features'
import Backends from './components/Backends'
import Stats from './components/Stats'
import FAQ from './components/FAQ'
import Footer from './components/Footer'

export default function App() {
  return (
    <>
      <Header />

      <section className="hero">
        <h1>Animated tech <span>ghost overlay</span></h1>
        <p>
          Full-screen cyberpunk holographic screensaver for Linux &amp; Windows.
          Toggle on/off with <kbd>Ctrl</kbd>+<kbd>3</kbd>.
        </p>

        <InstallSection />

        <div className="demo-placeholder">
          <span>▶ Ghost Screen in action</span>
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
