import { Badge } from '@/components/ui/badge'

const backends = [
  { name: 'X11 (Linux)', deps: 'tkinter', status: 'Stable' },
  { name: 'Wayland (Linux)', deps: 'GTK3 (gir)', status: 'Stable' },
  { name: 'Windows', deps: 'tkinter + ctypes', status: 'Stable' },
]

export default function Backends() {
  return (
    <section className="py-24 px-6 border-t border-border" id="backends">
      <div className="max-w-3xl mx-auto">
        <h2 className="text-3xl font-bold text-center mb-4">Platforms</h2>
        <p className="text-muted-foreground text-center max-w-xl mx-auto mb-12">
          Ghost Screen auto-detects your platform and uses the appropriate backend.
        </p>
        <div className="overflow-hidden border border-border rounded-lg">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-muted">
                <th className="text-left px-5 py-3 font-medium text-muted-foreground">Platform</th>
                <th className="text-left px-5 py-3 font-medium text-muted-foreground hidden sm:table-cell">Dependencies</th>
                <th className="text-right px-5 py-3 font-medium text-muted-foreground">Status</th>
              </tr>
            </thead>
            <tbody>
              {backends.map(b => (
                <tr key={b.name} className="border-t border-border">
                  <td className="px-5 py-3.5 font-medium text-accent">{b.name}</td>
                  <td className="px-5 py-3.5 text-muted-foreground hidden sm:table-cell">{b.deps}</td>
                  <td className="px-5 py-3.5 text-right">
                    <Badge variant="secondary" className="bg-accent-dim/30 text-accent border-0 font-mono text-xs">{b.status}</Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  )
}
