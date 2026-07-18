import { useState } from 'react'

const installs = {
  curl: { label: 'curl', cmd: 'curl -fsSL https://raw.githubusercontent.com/jsticks779/Ghost-Screen/main/install.sh | bash' },
  npm: { label: 'npm', cmd: 'npm install -g ghost-screen' },
  powershell: { label: 'PowerShell', cmd: 'powershell -Command "iex ((New-Object Net.WebClient).DownloadString(\'https://raw.githubusercontent.com/jsticks779/Ghost-Screen/main/install.ps1\'))"' },
  git: { label: 'git', cmd: 'git clone https://github.com/jsticks779/Ghost-Screen.git\ncd Ghost-Screen\npython ghost_screen.py' },
}

type Key = keyof typeof installs

export default function InstallSection() {
  const [tab, setTab] = useState<Key>('curl')
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    await navigator.clipboard.writeText(installs[tab].cmd)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="install-section">
      <div className="install-tabs">
        {(Object.keys(installs) as Key[]).map(k => (
          <button
            key={k}
            className={`install-tab${tab === k ? ' active' : ''}`}
            onClick={() => { setTab(k); setCopied(false) }}
          >
            {installs[k].label}
          </button>
        ))}
      </div>
      <div className="install-block">
        <code>{installs[tab].cmd}</code>
        <button className={`copy-btn${copied ? ' copied' : ''}`} onClick={handleCopy}>
          {copied ? 'Copied' : 'Copy'}
        </button>
      </div>
    </div>
  )
}
