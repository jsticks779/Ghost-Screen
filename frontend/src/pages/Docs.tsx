import { useState, useEffect } from 'react'
import { useLocation, Link } from 'react-router-dom'
import { ChevronDown, House, Menu, X } from 'lucide-react'
import Header from '@/components/Header'
import Footer from '@/components/Footer'

const sections = [
  {
    id: 'intro',
    label: 'Intro',
  },
  {
    id: 'installation',
    label: 'Installation',
    subs: [
      { id: 'install-linux', label: 'Linux' },
      { id: 'install-windows', label: 'Windows' },
    ],
  },
  {
    id: 'usage',
    label: 'Usage',
    subs: [
      { id: 'usage-basic', label: 'Basic usage' },
      { id: 'usage-shortcut', label: 'Toggle shortcut' },
      { id: 'usage-screensaver', label: 'Screensaver mode' },
    ],
  },
  {
    id: 'configuration',
    label: 'Configuration',
    subs: [
      { id: 'config-run', label: 'Run Ghost Screen' },
      { id: 'config-shortcut', label: 'Change shortcut' },
      { id: 'config-wallpaper', label: 'Wallpaper / Image / Video' },
      { id: 'config-color', label: 'Change color' },
      { id: 'config-check', label: 'Check status' },
      { id: 'config-autostart', label: 'Autostart' },
      { id: 'config-commands', label: 'All commands' },
    ],
  },
]

function flattenSections(secs: typeof sections): { id: string; label: string }[] {
  const flat: { id: string; label: string }[] = []
  for (const s of secs) {
    flat.push({ id: s.id, label: s.label })
    if (s.subs) for (const sub of s.subs) flat.push({ id: sub.id, label: sub.label })
  }
  return flat
}

function CodeBlock({ label, code }: { label?: string; code: string }) {
  return (
    <div className="mb-6">
      {label && (
        <div className="bg-muted rounded-t-lg border border-border border-b-0 px-4 py-2 text-xs text-muted-foreground font-mono">
          {label}
        </div>
      )}
      <pre className={`text-sm bg-card border border-border ${label ? 'rounded-b-lg' : 'rounded-lg'} p-4 overflow-x-auto font-mono leading-relaxed scrollbar-none max-w-full`}>
        {code}
      </pre>
    </div>
  )
}

function TipBox({ children }: { children: React.ReactNode }) {
  return (
    <div className="bg-card border-l-4 border-accent rounded-r-lg p-4 mb-6">
      <p className="text-sm text-foreground font-medium mb-1">Tip</p>
      <p className="text-sm text-muted-foreground">{children}</p>
    </div>
  )
}

export default function Docs() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [expanded, setExpanded] = useState<string[]>(['intro', 'installation', 'usage', 'configuration'])
  const location = useLocation()

  const flatItems = flattenSections(sections)

  useEffect(() => {
    setSidebarOpen(false)
  }, [location])

  const toggleSub = (id: string) => {
    setExpanded(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id])
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Header />

      {/* Mobile header */}
      <div className="md:hidden sticky top-17 z-30 flex items-center justify-between border-b border-border px-4 py-3 bg-background">
        <button onClick={() => setSidebarOpen(!sidebarOpen)} className="text-muted-foreground hover:text-foreground" aria-label="Menu">
          {sidebarOpen ? <X size={22} /> : <Menu size={22} />}
        </button>
        <span className="text-sm font-medium">Documentation</span>
        <div className="w-6" />
      </div>

      <div className="flex-1 flex overflow-x-hidden">
        {/* Sidebar overlay on mobile */}
        {sidebarOpen && (
          <div className="md:hidden fixed inset-0 z-40 bg-background/80" onClick={() => setSidebarOpen(false)} />
        )}

        {/* Sidebar */}
        <aside className={`${sidebarOpen ? 'fixed inset-y-0 left-0 z-50 w-64 shadow-xl' : 'hidden'} md:fixed md:top-17 md:block w-60 h-[calc(100vh-4.25rem)] flex-shrink-0 border-r border-border bg-background overflow-y-auto scrollbar-none`}>
          <nav className="px-4 py-6">
            {/* Mobile X button */}
            <div className="md:hidden flex items-center justify-between mb-4 pb-4 border-b border-border">
              <Link to="/" onClick={() => setSidebarOpen(false)} className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors">
                <House size={16} /> Home
              </Link>
              <button onClick={() => setSidebarOpen(false)} className="text-muted-foreground hover:text-foreground" aria-label="Close menu">
                <X size={20} />
              </button>
            </div>

            <div className="flex flex-col gap-1">
              {sections.map(sec => {
                const isExpanded = expanded.includes(sec.id)
                return (
                  <div key={sec.id}>
                    <button
                      onClick={() => {
                        if (sec.subs) { toggleSub(sec.id) }
                        else { setSidebarOpen(false); document.getElementById(sec.id)?.scrollIntoView({ behavior: 'smooth' }) }
                      }}
                      className={`flex items-center justify-between w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                        sec.subs ? 'font-medium text-foreground' : 'text-muted-foreground hover:text-foreground hover:bg-muted'
                      }`}
                    >
                      <a href={`#${sec.id}`} onClick={e => e.stopPropagation()} className="flex-1">{sec.label}</a>
                      {sec.subs && (
                        <ChevronDown size={14} className={`transition-transform ${isExpanded ? 'rotate-0' : '-rotate-90'}`} />
                      )}
                    </button>
                    {sec.subs && isExpanded && (
                      <div className="ml-3 mt-1 mb-1 flex flex-col gap-0.5 border-l border-border pl-3">
                        {sec.subs.map(sub => (
                          <a
                            key={sub.id}
                            href={`#${sub.id}`}
                            onClick={() => setSidebarOpen(false)}
                            className="text-sm text-muted-foreground hover:text-foreground transition-colors py-1.5 px-2 rounded-md hover:bg-muted"
                          >
                            {sub.label}
                          </a>
                        ))}
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          </nav>
        </aside>

        {/* Main content */}
        <main className="flex-1 min-w-0 max-w-3xl mx-auto px-6 py-12 md:ml-60">
          {/* Intro */}
          <section id="intro" className="mb-20">
            <h1 className="text-3xl font-bold mb-2">Intro</h1>
            <p className="text-base text-muted-foreground mb-6">Get started with Ghost Screen.</p>
            <p className="text-sm text-muted-foreground mb-10 leading-relaxed">
              Ghost Screen is an open source desktop overlay that secures your screen with a single shortcut.
              It works on Linux and Windows with zero external dependencies.
            </p>

            <div className="mb-8 rounded-lg overflow-hidden border border-border">
              <img src="/Doc%20image.png" alt="Ghost Screen" className="w-full" />
            </div>

            <p className="text-sm font-medium">Let&apos;s get started.</p>
          </section>

          <hr className="border-border mb-20" />

          {/* Installation */}
          <section id="installation" className="mb-20">
            <h2 className="text-2xl font-bold mb-8">Installation</h2>

            {/* Linux */}
            <section id="install-linux" className="mb-12">
              <h3 className="text-lg font-semibold mb-4">Linux</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Open your terminal and paste the command below. It will download and install Ghost Screen automatically.
              </p>
              <CodeBlock label="Terminal window" code="curl -fsSL https://raw.githubusercontent.com/jsticks779/Ghost-Screen/main/install.sh | bash" />
              <p className="text-sm text-muted-foreground mb-4">
                After installation, press <kbd className="px-1.5 py-0.5 text-xs font-mono bg-muted border border-border rounded">Ctrl</kbd>+<kbd className="px-1.5 py-0.5 text-xs font-mono bg-muted border border-border rounded">3</kbd> to toggle Ghost Screen.
              </p>
              <h4 className="text-sm font-medium text-accent mb-2">Uninstall</h4>
              <CodeBlock label="Terminal window" code="curl -fsSL https://raw.githubusercontent.com/jsticks779/Ghost-Screen/main/uninstall.sh | bash" />
            </section>

            {/* Windows */}
            <section id="install-windows" className="mb-12">
              <h3 className="text-lg font-semibold mb-4">Windows</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Open Command Prompt or PowerShell as administrator and paste the command below.
              </p>
              <CodeBlock label="Command Prompt" code='powershell -c "irm https://raw.githubusercontent.com/jsticks779/Ghost-Screen/main/install.ps1 | iex"' />
              <p className="text-sm text-muted-foreground mb-4">
                After installation, press <kbd className="px-1.5 py-0.5 text-xs font-mono bg-muted border border-border rounded">Ctrl</kbd>+<kbd className="px-1.5 py-0.5 text-xs font-mono bg-muted border border-border rounded">3</kbd> to toggle Ghost Screen.
              </p>
              <h4 className="text-sm font-medium text-accent mb-2">Uninstall</h4>
              <CodeBlock label="PowerShell" code='powershell -c "Remove-Item -Recurse \"$env:LOCALAPPDATA\GhostScreen\" -Force"' />
            </section>
          </section>

          <hr className="border-border mb-20" />

          {/* Usage */}
          <section id="usage" className="mb-20">
            <h2 className="text-2xl font-bold mb-8">Usage</h2>

            <section id="usage-basic" className="mb-10">
              <h3 className="text-lg font-semibold mb-4">Basic usage</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Run Ghost Screen by typing the command below in your terminal. Once running, press the toggle shortcut to show or hide the overlay.
              </p>
              <CodeBlock label="Terminal window" code="ghost-screen" />
              <p className="text-sm text-muted-foreground">
                The overlay will appear full-screen, blocking all input until you toggle it off.
              </p>
            </section>

            <section id="usage-shortcut" className="mb-10">
              <h3 className="text-lg font-semibold mb-4">Toggle shortcut</h3>
              <p className="text-sm text-muted-foreground mb-4">
                The default shortcut is <kbd className="px-1.5 py-0.5 text-xs font-mono bg-muted border border-border rounded">Ctrl</kbd>+<kbd className="px-1.5 py-0.5 text-xs font-mono bg-muted border border-border rounded">3</kbd>. Press it again to close the overlay.
              </p>
              <p className="text-sm text-muted-foreground mb-4">
                To change the shortcut, see the Configuration section below.
              </p>
              <TipBox>
                If the shortcut does not work, run <code className="text-accent text-xs font-mono bg-muted px-1.5 py-0.5 rounded">ghost-screen --check</code> to see what went wrong.
              </TipBox>
            </section>

            <section id="usage-screensaver" className="mb-10">
              <h3 className="text-lg font-semibold mb-4">Screensaver mode</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Ghost Screen can automatically activate after a period of inactivity.
              </p>
              <CodeBlock label="Terminal window" code="ghost-screen --idle 5" />
              <p className="text-sm text-muted-foreground">
                This will activate the overlay after 5 minutes of idle time. Press the toggle shortcut to dismiss it.
              </p>
            </section>
          </section>

          <hr className="border-border mb-20" />

          {/* Configuration */}
          <section id="configuration" className="mb-20">
            <h2 className="text-2xl font-bold mb-8">Configuration</h2>

            <section id="config-run" className="mb-10">
              <h3 className="text-lg font-semibold mb-4">Run Ghost Screen</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Simply run <code className="text-accent text-xs font-mono bg-muted px-1.5 py-0.5 rounded">ghost-screen</code> in your terminal. The first time, it will open the overlay immediately.
              </p>
              <CodeBlock label="Terminal window" code="ghost-screen" />
              <p className="text-sm text-muted-foreground">
                Running the command again will toggle the overlay off. Use <code className="text-accent text-xs font-mono bg-muted px-1.5 py-0.5 rounded">ghost-screen --kill</code> to stop the process entirely.
              </p>
            </section>

            <section id="config-shortcut" className="mb-10">
              <h3 className="text-lg font-semibold mb-4">Change shortcut</h3>
              <p className="text-sm text-muted-foreground mb-4">
                You can change the toggle shortcut to any key combination you like.
              </p>
              <CodeBlock label="Terminal window" code="ghost-screen --shortcut Ctrl+Shift+G" />
              <p className="text-sm text-muted-foreground">
                This sets the shortcut to <kbd className="px-1.5 py-0.5 text-xs font-mono bg-muted border border-border rounded">Ctrl</kbd>+<kbd className="px-1.5 py-0.5 text-xs font-mono bg-muted border border-border rounded">Shift</kbd>+<kbd className="px-1.5 py-0.5 text-xs font-mono bg-muted border border-border rounded">G</kbd>. You can use any combination of Ctrl, Shift, Alt, and a key.
              </p>
            </section>

            <section id="config-wallpaper" className="mb-10">
              <h3 className="text-lg font-semibold mb-4">Wallpaper / Image / Video</h3>
              <p className="text-sm text-muted-foreground mb-4">
                You can set a custom background image, video, or solid color to appear on Ghost Screen.
              </p>
              <CodeBlock label="Set an image or video as background" code="ghost-screen --set-bg /path/to/your/image.png" />
              <CodeBlock label="Set a solid color background" code="ghost-screen --set-bg-color \\#ff0088" />
              <p className="text-sm text-muted-foreground mb-4">
                The background will be applied the next time you open Ghost Screen. Supported formats: PNG, JPG, GIF, MP4, WEBM.
              </p>
              <TipBox>
                You can also set these permanently by editing <code className="text-accent text-xs font-mono bg-muted px-1.5 py-0.5 rounded">~/.config/ghost-screen/ghost_screen.json</code>. Add <code className="text-accent text-xs font-mono bg-muted px-1.5 py-0.5 rounded">&quot;background_image&quot;: &quot;/path/to/file&quot;</code> to the config.
              </TipBox>
            </section>

            <section id="config-color" className="mb-10">
              <h3 className="text-lg font-semibold mb-4">Change color</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Ghost Screen has 9 color slots you can customize. Each is a hex color value.
              </p>
              <CodeBlock label="Set primary color" code='ghost-screen --set-color primary "#ff0088"' />
              <p className="text-sm text-muted-foreground mb-2">Available color keys:</p>
              <ul className="text-sm text-muted-foreground mb-4 list-disc list-inside space-y-1">
                <li><code className="text-accent text-xs font-mono bg-muted px-1.5 py-0.5 rounded">primary</code> — main cyan color</li>
                <li><code className="text-accent text-xs font-mono bg-muted px-1.5 py-0.5 rounded">secondary</code> — secondary pink</li>
                <li><code className="text-accent text-xs font-mono bg-muted px-1.5 py-0.5 rounded">accent</code> — accent blue</li>
                <li><code className="text-accent text-xs font-mono bg-muted px-1.5 py-0.5 rounded">particle</code> — particle color</li>
                <li><code className="text-accent text-xs font-mono bg-muted px-1.5 py-0.5 rounded">ghost_fill</code> — ghost body fill</li>
                <li><code className="text-accent text-xs font-mono bg-muted px-1.5 py-0.5 rounded">ghost_outline</code> — ghost outline</li>
                <li><code className="text-accent text-xs font-mono bg-muted px-1.5 py-0.5 rounded">bg</code> — background color</li>
                <li><code className="text-accent text-xs font-mono bg-muted px-1.5 py-0.5 rounded">grid</code> — grid lines</li>
                <li><code className="text-accent text-xs font-mono bg-muted px-1.5 py-0.5 rounded">glow</code> — glow effect</li>
              </ul>
              <p className="text-sm text-muted-foreground">
                You can also edit the config file directly to set all colors at once.
              </p>
            </section>

            <section id="config-check" className="mb-10">
              <h3 className="text-lg font-semibold mb-4">Check status</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Use the check command to verify dependencies and see diagnostic info.
              </p>
              <CodeBlock label="Terminal window" code="ghost-screen --check" />
              <p className="text-sm text-muted-foreground mb-4">
                This will show your platform, Python version, display server, and which dependencies are installed.
              </p>
              <CodeBlock label="Terminal window" code="ghost-screen --version" />
            </section>

            <section id="config-autostart" className="mb-10">
              <h3 className="text-lg font-semibold mb-4">Autostart</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Ghost Screen can start automatically when you log in.
              </p>
              <CodeBlock label="Enable autostart" code="ghost-screen --autostart enable" />
              <CodeBlock label="Disable autostart" code="ghost-screen --autostart disable" />
              <CodeBlock label="Check autostart status" code="ghost-screen --autostart status" />
            </section>

            <section id="config-commands" className="mb-10">
              <h3 className="text-lg font-semibold mb-4">All commands</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Here is the full list of Ghost Screen commands:
              </p>
              <CodeBlock label="Terminal window" code={
`ghost-screen                  Toggle overlay on/off
ghost-screen --kill           Kill running instance
ghost-screen --version        Show version
ghost-screen --check          Check dependencies
ghost-screen --shortcut COMBO Set toggle shortcut (e.g. Ctrl+Shift+G)
ghost-screen --set-bg PATH    Set background image/video
ghost-screen --set-bg-color C Set background color (e.g. #ff0088)
ghost-screen --set-color K C  Set a color key (e.g. primary #00fff7)
ghost-screen --autostart ...  Manage autostart (enable|disable|status)
ghost-screen --idle MIN       Screensaver mode (activate after N min)
ghost-screen --reset-config   Reset config to defaults`}
              />
            </section>
          </section>

          {/* Footer links */}
          <hr className="border-border mb-16" />
          <div className="flex flex-wrap gap-6 text-sm text-muted-foreground">
            <a href={`https://github.com/jsticks779/Ghost-Screen/edit/main/frontend/src/pages/Docs.tsx`} target="_blank" rel="noopener noreferrer" className="hover:text-foreground transition-colors">Edit this page</a>
            <a href="https://github.com/jsticks779/Ghost-Screen/issues/new" target="_blank" rel="noopener noreferrer" className="hover:text-foreground transition-colors">Found a bug? Open an issue</a>
            <a href="https://github.com/jsticks779/Ghost-Screen" target="_blank" rel="noopener noreferrer" className="hover:text-foreground transition-colors">GitHub</a>
          </div>
        </main>
      </div>
      <Footer />
    </div>
  )
}
