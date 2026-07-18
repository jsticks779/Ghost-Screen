import { Monitor, Lock, Moon, Wrench, Palette, Keyboard, Clock, Rocket } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'

const features = [
  { icon: Monitor, title: 'Full-screen overlay', desc: 'Animated cyberpunk ghost that covers all monitors. Toggle on/off with Ctrl+3.' },
  { icon: Lock, title: 'Input blocking', desc: 'Keyboard, mouse, and touch input are fully blocked while the ghost is active.' },
  { icon: Moon, title: 'Sleep inhibition', desc: 'Blocks sleep and screen blanking automatically. Toggle off to allow sleep.' },
  { icon: Wrench, title: 'Cross-platform', desc: 'Works on Linux (X11 & Wayland) and Windows. Auto-detects your platform.' },
  { icon: Palette, title: 'Customizable', desc: 'Change colors, opacity, speed, particle count via JSON config file.' },
  { icon: Keyboard, title: 'Custom shortcut', desc: 'Change the toggle shortcut to any key combination you want.' },
  { icon: Clock, title: 'Idle watchdog', desc: 'Screensaver mode — auto-activates after N minutes of idle time.' },
  { icon: Rocket, title: 'Zero dependencies', desc: 'On Windows, only Python\'s built-in tkinter and ctypes are needed.' },
]

export default function Features() {
  return (
    <section className="py-24 px-6" id="features">
      <div className="max-w-5xl mx-auto">
        <h2 className="text-3xl font-bold text-center mb-4">Features</h2>
        <p className="text-muted-foreground text-center max-w-xl mx-auto mb-16">
          Everything you need for a cyberpunk holographic screensaver experience.
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {features.map(f => {
            const Icon = f.icon
            return (
              <Card key={f.title} className="bg-card border-border">
                <CardContent className="p-5">
                  <div className="mb-3 text-accent">
                    <Icon size={20} />
                  </div>
                  <h3 className="font-semibold text-sm mb-1.5">{f.title}</h3>
                  <p className="text-sm text-muted-foreground leading-relaxed">{f.desc}</p>
                </CardContent>
              </Card>
            )
          })}
        </div>
      </div>
    </section>
  )
}
