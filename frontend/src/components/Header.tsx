import { useState, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { House, Sun, Moon } from 'lucide-react'
import Logo from './Logo'

export default function Header() {
  const [open, setOpen] = useState(false)
  const [dark, setDark] = useState(() => (localStorage.getItem('theme') || 'dark') === 'dark')
  const location = useLocation()

  useEffect(() => {
    setOpen(false)
  }, [location])

  const toggleTheme = () => {
    const next = !dark
    setDark(next)
    const theme = next ? 'dark' : 'light'
    document.documentElement.className = theme
    localStorage.setItem('theme', theme)
  }

  return (
    <header className="sticky top-0 z-50 border-b border-border bg-background">
      <div className="flex items-center justify-between h-17 max-w-5xl mx-auto px-6">
        <Link to="/" className="flex items-center" onClick={() => setOpen(false)}>
          <Logo small />
        </Link>

        <nav className="hidden md:flex items-center gap-5">
          <Link to="/" className="text-muted-foreground hover:text-foreground transition-colors">
            <House size={18} />
          </Link>
          <a href="https://github.com/jsticks779/Ghost-Screen" target="_blank" rel="noopener noreferrer" className="text-sm text-muted-foreground hover:text-foreground transition-colors">GitHub</a>
          <Link to="/docs" className="text-sm text-muted-foreground hover:text-foreground transition-colors">Docs</Link>
          <a href="#faq" className="text-sm text-muted-foreground hover:text-foreground transition-colors">FAQ</a>
          <button onClick={toggleTheme} className="text-muted-foreground hover:text-foreground transition-colors" aria-label="Toggle theme">
            {dark ? <Sun size={18} /> : <Moon size={18} />}
          </button>
        </nav>

        <button onClick={() => setOpen(!open)} className="md:hidden flex flex-col items-center justify-center w-8 h-8 gap-[5px]" aria-label="Menu">
          <span className={`block w-5 h-[2px] bg-foreground transition-all duration-200 ${open ? 'rotate-45 translate-y-[3.5px]' : ''}`} />
          <span className={`block w-5 h-[2px] bg-foreground transition-all duration-200 ${open ? '-rotate-45 -translate-y-[3.5px]' : ''}`} />
        </button>
      </div>

      <div className={`md:hidden absolute left-0 right-0 top-full overflow-hidden transition-all duration-300 ease-in-out ${open ? 'max-h-64 border-b border-border' : 'max-h-0'}`}>
        <div className="flex flex-col items-center gap-4 px-6 py-5 bg-background">
          <Link to="/" onClick={() => setOpen(false)} className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"><House size={16} /> Home</Link>
          <a href="https://github.com/jsticks779/Ghost-Screen" target="_blank" rel="noopener noreferrer" onClick={() => setOpen(false)} className="text-sm text-muted-foreground hover:text-foreground transition-colors">GitHub</a>
          <Link to="/docs" onClick={() => setOpen(false)} className="text-sm text-muted-foreground hover:text-foreground transition-colors">Docs</Link>
          <a href="#faq" onClick={() => setOpen(false)} className="text-sm text-muted-foreground hover:text-foreground transition-colors">FAQ</a>
          <button onClick={() => { toggleTheme(); setOpen(false) }} className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors">
            {dark ? <Sun size={16} /> : <Moon size={16} />} {dark ? 'Light' : 'Dark'} mode
          </button>
        </div>
      </div>
    </header>
  )
}
