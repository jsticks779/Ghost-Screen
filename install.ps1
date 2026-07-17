#!/usr/bin/env pwsh
<#
.SYNOPSIS
  Install Ghost Screen on Windows
.DESCRIPTION
  Installs Python (if missing), pywin32 + pillow, and the ghost-screen script.
  Can be run via: iex ((New-Object Net.WebClient).DownloadString('URL'))
#>

$REPO = "https://raw.githubusercontent.com/jsticks779/Ghost-Screen/main"
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
    # Refresh PATH
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "User") + ";" +
                [System.Environment]::GetEnvironmentVariable("Path", "Machine")
    Write-Host "    Python installed." -ForegroundColor Green
}

# ── Ensure pip packages ────────────────────────────────────────────────
Write-Host "    Installing Python packages (pywin32, pillow)..." -ForegroundColor Yellow
try {
    & $pythonExe -m pip install pywin32 pillow --quiet --upgrade 2>&1 | Out-Null
    Write-Host "    Packages installed." -ForegroundColor Green
} catch {
    Write-Host "    Failed to install packages. Run manually: pip install pywin32 pillow" -ForegroundColor Red
    exit 1
}

# ── Download script ────────────────────────────────────────────────────
Write-Host "    Downloading ghost_screen.py..." -ForegroundColor Yellow
if (-not (Test-Path $INSTALL_DIR)) {
    New-Item -ItemType Directory -Path $INSTALL_DIR -Force | Out-Null
}
try {
    Invoke-WebRequest -Uri "$REPO/$SCRIPT_NAME" -OutFile $SCRIPT_PATH
    Write-Host "    Script downloaded to $SCRIPT_PATH" -ForegroundColor Green
} catch {
    Write-Host "    Failed to download script. Check internet connection." -ForegroundColor Red
    exit 1
}

# ── Create launcher cmd ────────────────────────────────────────────────
$cmdContent = "@echo off`r`n""%~dp0..\..\..\Python312\python.exe"" ""$SCRIPT_PATH"" %*`r`n"
# Try to find the actual Python path
$pyPath = (Get-Command $pythonExe -ErrorAction SilentlyContinue).Source
if ($pyPath) {
    $cmdContent = "@echo off`r`n""$pyPath"" ""$SCRIPT_PATH"" %*`r`n"
}
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
Write-Host "  Ghost Screen installed!" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Press  Ctrl+3  to toggle the ghost on/off"
Write-Host "  Run: ghost-screen --help"
Write-Host "  Uninstall: Remove-Item -Recurse '$INSTALL_DIR'"
Write-Host ""
