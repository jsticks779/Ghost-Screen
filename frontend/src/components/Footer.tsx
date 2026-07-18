export default function Footer() {
  return (
    <footer className="footer">
      <div className="footer-links">
        <a href="https://github.com/jsticks779/Ghost-Screen">GitHub</a>
        <a href="#features">Features</a>
        <a href="#faq">FAQ</a>
      </div>
      <div>
        © {new Date().getFullYear()} Ghost Screen — MIT License
      </div>
    </footer>
  )
}
