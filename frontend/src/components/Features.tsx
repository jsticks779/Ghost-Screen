import { Monitor, Lock, Image } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'

const features = [
  {
    icon: Monitor,
    title: 'Full-screen overlay',
    desc: 'Ghost Screen will toggle on and off fully on a screen by pressing default shortcut, or the one you will create.',
  },
  {
    icon: Lock,
    title: 'Input blocking',
    desc: 'Toggling of Ghost Screen will cause blocking of any input for your security until you toggle off Ghost Screen to continue using desktop.',
  },
  {
    icon: Image,
    title: 'Customizable',
    desc: 'You can change image, video, wallpaper to appear on Ghost Screen any time you want.',
  },
]

export default function Features() {
  return (
    <section className="py-24 px-6" id="features">
      <div className="max-w-4xl mx-auto">
        <h2 className="text-3xl font-bold text-center mb-16">Features</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {features.map(f => {
            const Icon = f.icon
            return (
              <Card key={f.title} className="bg-card border-border">
                <CardContent className="p-6 text-center">
                  <div className="mb-4 text-accent flex justify-center">
                    <Icon size={28} />
                  </div>
                  <h3 className="font-semibold text-base mb-2">{f.title}</h3>
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
