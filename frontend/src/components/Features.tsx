import { Monitor, Lock, Moon, Wrench, Palette, Keyboard, Clock, Rocket } from 'lucide-react'

const features = [
  { icon: Monitor, title: 'Full-screen overlay', desc: 'Animated cyberpunk ghost that covers all monitors. Toggle on/off with Ctrl+3.' },
  { icon: Lock, title: 'Input blocking', desc: 'Keyboard, mouse, and touch input are fully blocked while the ghost is active.' },
  { icon: Moon, title: 'Sleep inhibition', desc: 'Blocks sleep and screen blanking automatically. Toggle off to allow sleep.' },
  { icon: Wrench, title: 'Cross-platform', desc: 'Works on Linux (X11 & Wayland) and Windows. Auto-detects your platform.' },
  { icon: Palette, title: 'Customizable', desc: 'Change colors, opacity, speed, particle count via JSON config file.' },
  { icon: Keyboard, title: 'Custom shortcut', desc: 'Change the toggle shortcut to any key combination you want.' },
  { icon: Clock, title: 'Idle watchdog', desc: 'Screensaver mode — auto-activates after N minutes of idle time.' },
  { icon: Rocket, title: 'Zero dependencies', desc: 'On Windows, only Python\'s built-in tkinter and ctypes are needed — no pip install required.' },
]

export default function Features() {
  return (
    <section className="section" id="features">
      <h2 className="section-title">Features</h2>
      <p className="section-sub">
        Everything you need for a cyberpunk holographic screensaver experience.
      </p>
      <div className="features container">
        {features.map(f => {
          const Icon = f.icon
          return (
            <div key={f.title} className="feature-card">
              <div className="feature-icon"><Icon size={24} /></div>
              <h3>{f.title}</h3>
              <p>{f.desc}</p>
            </div>
          )
        })}
      </div>
    </section>
  )
}
