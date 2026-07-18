const backends = [
  { platform: 'Windows', backend: 'tkinter + ctypes', blocking: 'WH_KEYBOARD_LL / WH_MOUSE_LL hooks', deps: 'Built into Python — none needed' },
  { platform: 'Linux (X11)', backend: 'tkinter', blocking: 'grab_set_global()', deps: 'python3-tk' },
  { platform: 'Linux (Wayland)', backend: 'GTK3 + Pillow', blocking: 'zwp_keyboard_shortcuts_inhibit + seat grab', deps: 'python3-gi, gir1.2-gtk-3.0, python3-pil' },
]

export default function Backends() {
  return (
    <section className="section" id="backends">
      <h2 className="section-title">Platform Support</h2>
      <p className="section-sub">
        Ghost Screen auto-detects your platform and picks the right backend.
      </p>
      <div className="container" style={{ overflowX: 'auto' }}>
        <table className="backends-table">
          <thead>
            <tr>
              <th>Platform</th>
              <th>Backend</th>
              <th>Input Blocking</th>
              <th>Dependencies</th>
            </tr>
          </thead>
          <tbody>
            {backends.map(b => (
              <tr key={b.platform}>
                <td>{b.platform}</td>
                <td>{b.backend}</td>
                <td>{b.blocking}</td>
                <td>{b.deps}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}
