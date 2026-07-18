param()

$OWNER = "jsticks779"
$REPO_NAME = "Ghost-Screen"
$SCRIPT_NAME = "ghost_screen.py"
$INSTALL_DIR = "$env:LOCALAPPDATA\GhostScreen"
$SCRIPT_PATH = "$INSTALL_DIR\$SCRIPT_NAME"
$CMD_NAME = "ghost-screen.cmd"
$CMD_PATH = "$INSTALL_DIR\$CMD_NAME"

Write-Host "==> Installing Ghost Screen..." -ForegroundColor Cyan

# ── Check / install Python ─────────────────────────────────────────────
$python = (Get-Command python3 -ErrorAction SilentlyContinue) -or
          (Get-Command python -ErrorAction SilentlyContinue)
$pythonExe = "python"

if (-not $python) {
    Write-Host "    Python not found. Downloading Python installer..." -ForegroundColor Yellow
    $pyInstaller = "$env:TEMP\python-installer.exe"
    Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.12.5/python-3.12.5-amd64.exe" -OutFile $pyInstaller
    Write-Host "    Running Python installer (check 'Add to PATH' when prompted)..." -ForegroundColor Yellow
    Start-Process -Wait -FilePath $pyInstaller -ArgumentList "/quiet", "InstallAllUsers=0", "PrependPath=1"
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "User") + ";" +
                [System.Environment]::GetEnvironmentVariable("Path", "Machine")
    Write-Host "    Python installed." -ForegroundColor Green
}

# ── Download script ────────────────────────────────────────────────────
Write-Host "    Downloading ghost_screen.py..." -ForegroundColor Yellow
if (-not (Test-Path $INSTALL_DIR)) {
    New-Item -ItemType Directory -Path $INSTALL_DIR -Force | Out-Null
}
try {
    $apiUrl = "https://api.github.com/repos/$OWNER/$REPO_NAME/contents/$SCRIPT_NAME"
    Invoke-WebRequest -Uri $apiUrl -Headers @{"Accept"="application/vnd.github.v3.raw"} -OutFile $SCRIPT_PATH
    Write-Host "    Script downloaded to $SCRIPT_PATH" -ForegroundColor Green
    # Download logo for terminal display
    $logoUrl = "https://api.github.com/repos/$OWNER/$REPO_NAME/contents/logo.svg"
    $logoSvg = Join-Path $INSTALL_DIR "logo.svg"
    try {
        Invoke-WebRequest -Uri $logoUrl -Headers @{"Accept"="application/vnd.github.v3.raw"} -OutFile $logoSvg 2>$null
    } catch {}
} catch {
    Write-Host "    Failed to download script. Check internet connection." -ForegroundColor Red
    exit 1
}

# ── Create launcher cmd ────────────────────────────────────────────────
$pyPath = (Get-Command $pythonExe -ErrorAction SilentlyContinue).Source
$cmdContent = "@echo off`r`n""$pyPath"" ""$SCRIPT_PATH"" %*`r`n"
Set-Content -Path $CMD_PATH -Value $cmdContent
Write-Host "    Launcher created: $CMD_PATH" -ForegroundColor Green

# ── Add to PATH ────────────────────────────────────────────────────────
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($currentPath -notlike "*$INSTALL_DIR*") {
    [Environment]::SetEnvironmentVariable("Path", "$currentPath;$INSTALL_DIR", "User")
    $env:Path += ";$INSTALL_DIR"
    Write-Host "    Added $INSTALL_DIR to PATH" -ForegroundColor Green
}

# ── Create shortcut in Start Menu ──────────────────────────────────────
try {
    $WshShell = New-Object -ComObject WScript.Shell
    $startMenu = [Environment]::GetFolderPath("StartMenu") + "\Programs\Ghost Screen"
    if (-not (Test-Path $startMenu)) {
        New-Item -ItemType Directory -Path $startMenu -Force | Out-Null
    }
    $shortcut = $WshShell.CreateShortcut("$startMenu\Ghost Screen.lnk")
    $shortcut.TargetPath = $pyPath
    $shortcut.Arguments = """$SCRIPT_PATH"""
    $shortcut.Description = "Toggle Ghost Screen overlay"
    $shortcut.Save()
    Write-Host "    Start menu shortcut created." -ForegroundColor Green
} catch {
    Write-Host "    Could not create start menu shortcut." -ForegroundColor DarkYellow
}

# ── Test ───────────────────────────────────────────────────────────────
try {
    $ver = & $pythonExe "$SCRIPT_PATH" --version 2>&1
    Write-Host "    $ver" -ForegroundColor Green
} catch {
    Write-Host "    Installation verification failed." -ForegroundColor Red
}

Write-Host ""
try {
    # Render SVG logo using Python (guaranteed to be installed)
    $logo_svg = Join-Path $INSTALL_DIR "logo.svg"
    if (Test-Path $logo_svg) {
        $pythonCode = @'
import xml.etree.ElementTree as ET, sys
C = "\033[38;2;0;255;247m"; R = "\033[0m"
try:
    t = ET.parse(sys.argv[1])
    r = t.getroot()
    ns = {"svg": "http://www.w3.org/2000/svg"}
    letters = {}
    for g in r.findall(".//svg:g", ns):
        gid = g.get("id", "")
        if gid.startswith("l") and gid[1:].isdigit():
            pts = [(int(float(a.get("x",0))), int(float(a.get("y",0)))) for a in g.findall("svg:rect", ns)]
            if pts: letters[int(gid[1:])] = pts
    def render(idx):
        pts = letters[idx]
        mx = min(p[0] for p in pts); Mx = max(p[0] for p in pts) + 10
        my = min(p[1] for p in pts); My = max(p[1] for p in pts) + 10
        g = [[0] * ((Mx - mx) // 10) for _ in range((My - my) // 10)]
        for x, y in pts: g[(y - my) // 10][(x - mx) // 10] = 1
        return [''.join('█' if g[r_][c_] else ' ' for c_ in range(len(g[0]))) for r_ in range(len(g))] + [' ' * len(g[0])] * (7 - len(g))
    grids = [render(i) for i in sorted(letters)]
    gid = [0,1,2,3,4]; sid = [5,6,7,8,9,10]
    for row in range(7):
        print(C + ' '.join(grids[i][row] for i in gid) + '  ' + ' '.join(grids[i][row] for i in sid) + R)
except:
    print("  Ghost Screen")
'@
        & $pythonExe -c $pythonCode $logo_svg 2>$null
    } else {
        Write-Host "  Ghost Screen" -ForegroundColor Cyan
    }
} catch {
    Write-Host "  Ghost Screen" -ForegroundColor Cyan
}
Write-Host ""
Write-Host "  Ghost Screen installed!" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Press  Ctrl+3  to toggle the ghost on/off"
Write-Host "  Run: ghost-screen --help"
Write-Host "  Uninstall: Remove-Item -Recurse '$INSTALL_DIR'"
Write-Host ""
