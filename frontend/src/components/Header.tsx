import { Menu } from 'lucide-react'
import Logo from './Logo'
import { Button } from '@/components/ui/button'

export default function Header() {
  return (
    <header className="sticky top-0 z-50 border-b border-border bg-background/95">
      <div className="flex items-center justify-between h-16 max-w-5xl mx-auto px-6">
        <a href="#" className="flex items-center">
          <Logo small />
        </a>
        <nav className="hidden sm:flex items-center gap-6">
          <a href="#features" className="text-sm text-muted-foreground hover:text-foreground transition-colors">Features</a>
          <a href="#faq" className="text-sm text-muted-foreground hover:text-foreground transition-colors">FAQ</a>
          <a href="https://github.com/jsticks779/Ghost-Screen" target="_blank" rel="noopener noreferrer">
            <Button variant="outline" size="sm">GitHub</Button>
          </a>
        </nav>
        <button className="sm:hidden text-muted-foreground">
          <Menu size={20} />
        </button>
      </div>
    </header>
  )
}
