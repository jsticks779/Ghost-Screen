const stats = [
  { number: '1', label: 'Active User', suffix: '' },
  { number: '3', label: 'Backends', suffix: '' },
  { number: '0', label: 'Dependencies', suffix: '' },
]

export default function Stats() {
  return (
    <section className="py-16 px-6 border-t border-border">
      <div className="max-w-3xl mx-auto grid grid-cols-3 gap-8 text-center">
        {stats.map(s => (
          <div key={s.label}>
            <div className="text-3xl font-bold text-accent">{s.number}</div>
            <div className="text-sm text-muted-foreground mt-1">{s.label}</div>
          </div>
        ))}
      </div>
    </section>
  )
}
