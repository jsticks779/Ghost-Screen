import Header from '@/components/Header'
import Footer from '@/components/Footer'

const sections = [
  {
    title: 'Installation',
    items: [
      ['Linux (X11)', 'pip install ghost-screen\n\nOr clone the repo:\ngit clone https://github.com/jsticks779/Ghost-Screen.git\ncd Ghost-Screen\npip install -r requirements.txt'],
      ['Linux (Wayland)', 'Same as X11. GTK3 (gir) is required for Wayland:\nsudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0'],
      ['Windows', 'pip install ghost-screen\n\nNo external dependencies needed.\nUses Python built-in tkinter + ctypes.'],
    ],
  },
  {
    title: 'Usage',
    items: [
      ['Basic', 'python -m ghost_screen\n\nToggle the ghost overlay on/off with Ctrl+3.'],
      ['Config file', 'Create ~/.config/ghost-screen/config.json:\n{\n  "color": "#00fff7",\n  "opacity": 0.8,\n  "speed": 1.0,\n  "particles": 50\n}'],
      ['Shortcut', 'Change the toggle key in config.json:\n{\n  "shortcut": "ctrl+shift+g"\n}'],
      ['Idle watchdog', 'Auto-activate after N minutes of idle time:\n{\n  "idle_timeout": 5\n}'],
    ],
  },
  {
    title: 'Backends',
    items: [
      ['X11 (Linux)', 'Uses tkinter for the overlay window. Blocks keyboard and mouse via XGrabKeyboard/XGrabPointer.'],
      ['Wayland (Linux)', 'Uses GTK3 via PyGObject. Blocks input with gtk.grab_add().'],
      ['Windows', 'Uses tkinter + ctypes. Blocks input via low-level keyboard/mouse hooks (WH_KEYBOARD_LL, WH_MOUSE_LL).'],
    ],
  },
]

export default function Docs() {
  return (
    <>
      <Header />
      <main className="max-w-3xl mx-auto px-6 py-16">
        <h1 className="text-3xl font-bold mb-2">Documentation</h1>
        <p className="text-muted-foreground mb-12">Everything you need to know about Ghost Screen.</p>

        {sections.map(section => (
          <div key={section.title} className="mb-12">
            <h2 className="text-xl font-semibold mb-4">{section.title}</h2>
            <div className="flex flex-col gap-6">
              {section.items.map(([title, body]) => (
                <div key={title}>
                  <h3 className="text-sm font-medium text-accent mb-2">{title}</h3>
                  <pre className="text-sm text-muted-foreground bg-muted border border-border rounded-lg p-4 overflow-x-auto whitespace-pre-wrap font-mono leading-relaxed">
                    {body}
                  </pre>
                </div>
              ))}
            </div>
          </div>
        ))}

        <div className="border-t border-border pt-8 mt-12">
          <h2 className="text-xl font-semibold mb-4">Need help?</h2>
          <p className="text-muted-foreground">
            Open an issue on{' '}
            <a href="https://github.com/jsticks779/Ghost-Screen" target="_blank" rel="noopener noreferrer" className="text-accent hover:underline">GitHub</a>
            {' '}or check the{' '}
            <a href="#faq" className="text-accent hover:underline">FAQ</a>.
          </p>
        </div>
      </main>
      <Footer />
    </>
  )
}
