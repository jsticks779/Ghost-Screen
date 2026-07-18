import { Link } from 'react-router-dom'
import Logo from './Logo'

export default function Header() {
  return (
    <header className="sticky top-0 z-50 border-b border-border bg-background/95">
      <div className="flex items-center justify-between h-17 max-w-5xl mx-auto px-6">
        <Link to="/" className="flex items-center">
          <Logo small />
        </Link>
        <nav className="flex items-center gap-6">
          <a href="https://github.com/jsticks779/Ghost-Screen" target="_blank" rel="noopener noreferrer" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
            GitHub
          </a>
          <Link to="/docs" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
            Docs
          </Link>
          <a href="#faq" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
            FAQ
          </a>
        </nav>
      </div>
    </header>
  )
}
