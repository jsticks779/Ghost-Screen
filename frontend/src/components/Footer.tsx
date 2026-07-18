import { Link } from 'react-router-dom'

export default function Footer() {
  return (
    <footer className="border-t border-border py-10 px-6 text-center text-sm text-muted-foreground">
      <div className="flex justify-center gap-6 mb-4">
        <a href="https://github.com/jsticks779/Ghost-Screen" target="_blank" rel="noopener noreferrer" className="hover:text-foreground transition-colors">GitHub</a>
        <Link to="/docs" className="hover:text-foreground transition-colors">Docs</Link>
        <a href="#faq" className="hover:text-foreground transition-colors">FAQ</a>
      </div>
      <p>© {new Date().getFullYear()} Ghost Screen. MIT License.</p>
    </footer>
  )
}
