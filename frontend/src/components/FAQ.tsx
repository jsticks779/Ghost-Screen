import { useState } from 'react'

const faqs = [
  {
    q: 'What is Ghost Screen?',
    a: 'Ghost Screen is an open-source full-screen animated ghost overlay. It renders a cyberpunk holographic ghost on top of everything, blocking all input and preventing sleep — perfect as a screensaver or focus tool.',
  },
  {
    q: 'How do I toggle it?',
    a: 'Press Ctrl+3 to toggle the ghost on and off. On Windows, this is handled via a low-level keyboard hook. On Linux, it uses the system shortcut manager or the hook backend. You can change the shortcut with --shortcut "Ctrl+Shift+G".',
  },
  {
    q: 'Does it work on Wayland?',
    a: 'Yes! Ghost Screen fully supports Wayland via the GTK3 backend with zwp_keyboard_shortcuts_inhibit for input blocking. Tested on GNOME, KDE, Sway, Hyprland, River, COSMIC, and more.',
  },
  {
    q: 'What dependencies does Windows need?',
    a: 'None. The Windows backend uses only Python\'s built-in tkinter and ctypes modules. No pip install, no pywin32, no Pillow.',
  },
  {
    q: 'Does it prevent my PC from sleeping?',
    a: 'While active, sleep and screen blanking are blocked via SetThreadExecutionState on Windows and D-Bus logind / systemd-inhibit on Linux. Toggle off (Ctrl+3) to allow sleep again.',
  },
  {
    q: 'Can I customize the ghost appearance?',
    a: 'Yes. Create a ghost_screen.json file to change colors, opacity, animation speed, particle count, ghost size, and more. See the README for the full config reference.',
  },
  {
    q: 'Is it open source?',
    a: 'Yes, Ghost Screen is MIT-licensed. The full source code is on GitHub.',
  },
]

export default function FAQ() {
  const [open, setOpen] = useState<number | null>(null)

  return (
    <section className="section" id="faq">
      <h2 className="section-title">FAQ</h2>
      <p className="section-sub">Common questions about Ghost Screen.</p>
      <div className="faq-list">
        {faqs.map((faq, i) => (
          <div key={i} className="faq-item">
            <button className="faq-question" onClick={() => setOpen(open === i ? null : i)}>
              {faq.q}
              <span className={`faq-arrow${open === i ? ' open' : ''}`}>▾</span>
            </button>
            {open === i && <div className="faq-answer">{faq.a}</div>}
          </div>
        ))}
      </div>
    </section>
  )
}
