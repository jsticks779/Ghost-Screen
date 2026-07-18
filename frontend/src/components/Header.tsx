import { useState } from 'react'
import { Link } from 'react-router-dom'
import Logo from './Logo'

export default function Header() {
  const [open, setOpen] = useState(false)

  return (
    <header className="sticky top-0 z-50 border-b border-border bg-background/95">
      <div className="flex items-center justify-between h-17 max-w-5xl mx-auto px-6">
        <Link to="/" className="flex items-center" onClick={() => setOpen(false)}>
          <Logo small />
        </Link>

        <nav className="hidden md:flex items-center gap-6">
          <a href="https://github.com/jsticks779/Ghost-Screen" target="_blank" rel="noopener noreferrer" className="text-sm text-muted-foreground hover:text-foreground transition-colors">GitHub</a>
          <Link to="/docs" className="text-sm text-muted-foreground hover:text-foreground transition-colors">Docs</Link>
          <a href="#faq" className="text-sm text-muted-foreground hover:text-foreground transition-colors">FAQ</a>
        </nav>

        <button onClick={() => setOpen(!open)} className="md:hidden flex flex-col items-center justify-center w-8 h-8 gap-[5px]" aria-label="Menu">
          <span className={`block w-5 h-[2px] bg-foreground transition-transform ${open ? 'rotate-45 translate-y-[3.5px]' : ''}`} />
          <span className={`block w-5 h-[2px] bg-foreground transition-transform ${open ? '-rotate-45 -translate-y-[3.5px]' : ''}`} />
        </button>
      </div>

      {open && (
        <div className="md:hidden border-t border-border bg-background">
          <div className="flex flex-col items-center gap-4 py-5 px-6">
            <a href="https://github.com/jsticks779/Ghost-Screen" target="_blank" rel="noopener noreferrer" onClick={() => setOpen(false)} className="text-sm text-muted-foreground hover:text-foreground transition-colors">GitHub</a>
            <Link to="/docs" onClick={() => setOpen(false)} className="text-sm text-muted-foreground hover:text-foreground transition-colors">Docs</Link>
            <a href="#faq" onClick={() => setOpen(false)} className="text-sm text-muted-foreground hover:text-foreground transition-colors">FAQ</a>
          </div>
        </div>
      )}
    </header>
  )
}
