import { useState } from 'react'
import { Copy, Check } from 'lucide-react'

const installs = [
  { label: 'pip', cmd: 'pip install ghost-screen' },
  { label: 'git', cmd: 'git clone https://github.com/jsticks779/Ghost-Screen.git\ncd Ghost-Screen\npip install -r requirements.txt' },
  { label: 'curl', cmd: 'curl -fsSL https://ghost-screen.app/install | bash' },
]

export default function InstallSection() {
  const [tab, setTab] = useState(0)
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    await navigator.clipboard.writeText(installs[tab].cmd)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="max-w-md mx-auto mb-12">
      <div className="flex border border-border rounded-t-lg overflow-hidden">
        {installs.map((item, i) => (
          <button
            key={item.label}
            onClick={() => { setTab(i); setCopied(false) }}
            className={`flex-1 px-4 py-2.5 text-xs font-medium transition-colors font-mono ${
              tab === i
                ? 'bg-card text-accent'
                : 'bg-muted text-muted-foreground hover:text-foreground'
            } ${i > 0 ? 'border-l border-border' : ''}`}
          >
            {item.label}
          </button>
        ))}
      </div>
      <div className="flex items-center justify-between bg-card border border-t-0 border-border rounded-b-lg px-5 py-3">
        <code className="text-sm text-accent font-mono whitespace-pre-wrap">{installs[tab].cmd}</code>
        <button
          onClick={handleCopy}
          className="ml-3 p-1.5 text-muted-foreground hover:text-accent transition-colors flex-shrink-0"
        >
          {copied ? <Check size={16} /> : <Copy size={16} />}
        </button>
      </div>
    </div>
  )
}
