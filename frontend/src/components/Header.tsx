import Logo from './Logo'

export default function Header() {
  return (
    <header className="header">
      <div className="header-inner">
        <a href="#" className="header-logo">
          <Logo small />
          Ghost Screen
        </a>
        <nav className="header-nav">
          <a href="#features">Features</a>
          <a href="#backends">Platforms</a>
          <a href="#faq">FAQ</a>
          <a href="https://github.com/jsticks779/Ghost-Screen">GitHub</a>
        </nav>
      </div>
    </header>
  )
}
