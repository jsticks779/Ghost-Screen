const stats = [
  { number: '3', label: 'Platforms' },
  { number: '8', label: 'Linux compositors' },
  { number: '0', label: 'External deps (Windows)' },
]

export default function Stats() {
  return (
    <section className="section">
      <div className="container">
        <div className="stats-grid">
          {stats.map(s => (
            <div key={s.label} className="stat-card">
              <div className="stat-number">{s.number}</div>
              <div className="stat-label">{s.label}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
