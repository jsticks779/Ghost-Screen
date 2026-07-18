import Header from '@/components/Header'
import Footer from '@/components/Footer'

const sidebar = [
  {
    category: 'Getting Started',
    links: [
      { label: 'Installation', href: '#install' },
      { label: 'Usage', href: '#usage' },
      { label: 'Configuration', href: '#config' },
    ],
  },
  {
    category: 'Platforms',
    links: [
      { label: 'Linux (X11)', href: '#x11' },
      { label: 'Linux (Wayland)', href: '#wayland' },
      { label: 'Windows', href: '#windows' },
    ],
  },
  {
    category: 'Advanced',
    links: [
      { label: 'Custom shortcut', href: '#shortcut' },
      { label: 'Idle watchdog', href: '#watchdog' },
      { label: 'Backends', href: '#backends' },
    ],
  },
]

const toc = [
  { label: 'Installation', href: '#install' },
  { label: 'Usage', href: '#usage' },
  { label: 'Configuration', href: '#config' },
  { label: 'Backends', href: '#backends' },
]

export default function Docs() {
  const editUrl = `https://github.com/jsticks779/Ghost-Screen/edit/main/frontend/src/pages/Docs.tsx`
  const issueUrl = `https://github.com/jsticks779/Ghost-Screen/issues/new`

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <div className="flex-1 flex">
        {/* Sidebar */}
        <aside className="hidden lg:block w-60 flex-shrink-0 border-r border-border px-5 py-8">
          <nav className="flex flex-col gap-8">
            {sidebar.map(group => (
              <div key={group.category}>
                <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">
                  {group.category}
                </h3>
                <ul className="flex flex-col gap-2">
                  {group.links.map(link => (
                    <li key={link.href}>
                      <a
                        href={link.href}
                        className="text-sm text-muted-foreground hover:text-foreground transition-colors block py-1"
                      >
                        {link.label}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </nav>
        </aside>

        {/* Main content */}
        <main className="flex-1 max-w-3xl mx-auto px-6 py-12">
          <h1 className="text-3xl font-bold mb-2">Documentation</h1>
          <p className="text-muted-foreground mb-12">
            Everything you need to know about Ghost Screen.
          </p>

          {/* Install */}
          <section id="install" className="mb-16">
            <h2 className="text-xl font-semibold mb-4">Installation</h2>
            <div className="mb-6">
              <h3 className="text-sm font-medium text-accent mb-3">Linux (X11)</h3>
              <div className="bg-muted rounded-t-lg border border-border border-b-0 px-4 py-2 text-xs text-muted-foreground font-mono">Terminal window</div>
              <pre className="text-sm bg-card border border-border rounded-b-lg p-4 overflow-x-auto font-mono leading-relaxed">
pip install ghost-screen{'\n\n'}Or clone the repo:{'\n'}git clone https://github.com/jsticks779/Ghost-Screen.git{'\n'}cd Ghost-Screen{'\n'}pip install -r requirements.txt</pre>
            </div>
            <div className="mb-6">
              <h3 className="text-sm font-medium text-accent mb-3">Linux (Wayland)</h3>
              <div className="bg-muted rounded-t-lg border border-border border-b-0 px-4 py-2 text-xs text-muted-foreground font-mono">Terminal window</div>
              <pre className="text-sm bg-card border border-border rounded-b-lg p-4 overflow-x-auto font-mono leading-relaxed">
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0{'\n'}pip install ghost-screen</pre>
            </div>
            <div className="mb-6">
              <h3 className="text-sm font-medium text-accent mb-3">Windows</h3>
              <div className="bg-muted rounded-t-lg border border-border border-b-0 px-4 py-2 text-xs text-muted-foreground font-mono">Terminal window</div>
              <pre className="text-sm bg-card border border-border rounded-b-lg p-4 overflow-x-auto font-mono leading-relaxed">
pip install ghost-screen{'\n\n'}No external dependencies needed.{'\n'}Uses Python built-in tkinter + ctypes.</pre>
            </div>
          </section>

          <hr className="border-border mb-16" />

          {/* Usage */}
          <section id="usage" className="mb-16">
            <h2 className="text-xl font-semibold mb-4">Usage</h2>
            <div className="mb-6">
              <h3 className="text-sm font-medium text-accent mb-3">Basic</h3>
              <div className="bg-muted rounded-t-lg border border-border border-b-0 px-4 py-2 text-xs text-muted-foreground font-mono">Terminal window</div>
              <pre className="text-sm bg-card border border-border rounded-b-lg p-4 overflow-x-auto font-mono leading-relaxed">
python -m ghost_screen{'\n\n'}Toggle the ghost overlay on/off with Ctrl+3.</pre>
            </div>
            <div className="bg-card border-l-4 border-accent rounded-r-lg p-4 mb-6">
              <p className="text-sm text-foreground font-medium mb-1">Tip</p>
              <p className="text-sm text-muted-foreground">
                You can customize the toggle shortcut in the config file. See{' '}
                <a href="#config" className="text-accent hover:underline">Configuration</a>.
              </p>
            </div>
          </section>

          <hr className="border-border mb-16" />

          {/* Config */}
          <section id="config" className="mb-16">
            <h2 className="text-xl font-semibold mb-4">Configuration</h2>
            <p className="text-sm text-muted-foreground mb-6">
              Create <code className="text-accent text-xs font-mono bg-muted px-1.5 py-0.5 rounded">~/.config/ghost-screen/config.json</code> to customize:
            </p>
            <div className="bg-muted rounded-t-lg border border-border border-b-0 px-4 py-2 text-xs text-muted-foreground font-mono">config.json</div>
            <pre className="text-sm bg-card border border-border rounded-b-lg p-4 overflow-x-auto font-mono leading-relaxed">
{`{
  "color": "#00fff7",
  "opacity": 0.8,
  "speed": 1.0,
  "particles": 50
}`}</pre>
          </section>

          <hr className="border-border mb-16" />

          {/* Backends */}
          <section id="backends" className="mb-16">
            <h2 className="text-xl font-semibold mb-4">Backends</h2>
            <p className="text-sm text-muted-foreground mb-6">
              Ghost Screen auto-detects your platform and uses the appropriate backend.
            </p>
            <div className="overflow-hidden border border-border rounded-lg text-sm">
              <table className="w-full">
                <thead>
                  <tr className="bg-muted">
                    <th className="text-left px-5 py-3 font-medium text-muted-foreground">Platform</th>
                    <th className="text-left px-5 py-3 font-medium text-muted-foreground">Dependencies</th>
                    <th className="text-right px-5 py-3 font-medium text-muted-foreground">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {[
                    ['X11 (Linux)', 'tkinter', 'Stable'],
                    ['Wayland (Linux)', 'GTK3 (gir)', 'Stable'],
                    ['Windows', 'tkinter + ctypes', 'Stable'],
                  ].map(([platform, deps, status]) => (
                    <tr key={platform} className="border-t border-border">
                      <td className="px-5 py-3.5 font-medium text-accent">{platform}</td>
                      <td className="px-5 py-3.5 text-muted-foreground">{deps}</td>
                      <td className="px-5 py-3.5 text-right">
                        <span className="inline-flex items-center h-5 px-2 rounded-4xl text-xs font-medium bg-accent-dim/30 text-accent font-mono">
                          {status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          <hr className="border-border mb-16" />

          {/* Footer links */}
          <div className="flex flex-wrap gap-6 text-sm text-muted-foreground">
            <a href={editUrl} target="_blank" rel="noopener noreferrer" className="hover:text-foreground transition-colors">
              Edit this page
            </a>
            <a href={issueUrl} target="_blank" rel="noopener noreferrer" className="hover:text-foreground transition-colors">
              Found a bug? Open an issue
            </a>
            <a href="https://github.com/jsticks779/Ghost-Screen" target="_blank" rel="noopener noreferrer" className="hover:text-foreground transition-colors">
              GitHub
            </a>
          </div>
        </main>

        {/* On this page sidebar */}
        <aside className="hidden xl:block w-56 flex-shrink-0 px-5 py-12">
          <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-4">
            On this page
          </h3>
          <ul className="flex flex-col gap-2">
            {toc.map(item => (
              <li key={item.href}>
                <a
                  href={item.href}
                  className="text-sm text-muted-foreground hover:text-foreground transition-colors block py-1"
                >
                  {item.label}
                </a>
              </li>
            ))}
          </ul>
        </aside>
      </div>
      <Footer />
    </div>
  )
}
