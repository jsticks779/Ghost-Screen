#!/usr/bin/env node
const { execSync } = require("child_process");
const fs = require("fs");
const path = require("path");
const os = require("os");

const DIR = __dirname;
const IS_WIN = os.platform() === "win32";

function run(cmd, opts = {}) {
  try {
    return execSync(cmd, { cwd: DIR, stdio: "pipe", timeout: 30000, ...opts }).toString().trim();
  } catch {
    return "";
  }
}

function postinstall() {
  console.log("\n  Ghost Screen — npm postinstall");

  const isGlobal = process.env.npm_config_global === "true" ||
    process.argv.includes("global") ||
    __dirname.includes("node_modules/.pnpm") ||
    __dirname.includes("nvm") ||
    __dirname.includes("/usr/lib/node_modules") ||
    __dirname.includes("/usr/local/lib/node_modules");

  if (IS_WIN) {
    console.log("    Platform: Windows");
    // Install Python deps
    run('pip install pywin32 pillow --quiet --upgrade', { timeout: 60000 });
    // Ensure .py is executable via the npm bin shim (it handles shebangs)
    console.log("    Python packages installed (pywin32, pillow).");
    console.log('  Install complete!');
    console.log('  Run: npx ghost-screen');
    return;
  }

  // Linux build steps
  const hasGcc = run("command -v gcc");
  const hasWaylandScanner = run("command -v wayland-scanner");
  const xmlPath = path.join(DIR, "keyboard-shortcuts-inhibit-unstable-v1.xml");

  if (hasGcc && hasWaylandScanner && fs.existsSync(xmlPath)) {
    console.log("    Building Wayland keyboard shortcut inhibitor...");
    run("wayland-scanner client-header keyboard-shortcuts-inhibit-unstable-v1.xml zwp_ksh_client.h");
    run("wayland-scanner private-code keyboard-shortcuts-inhibit-unstable-v1.xml wl_ksh_code.c");
    const pkgConfig = run("pkg-config --cflags --libs gtk+-3.0 wayland-client");
    if (pkgConfig) {
      run(`gcc -shared -fPIC -o wl_inhibit.so wl_inhibit.c wl_ksh_code.c ${pkgConfig}`);
    }
  }

  if (hasGcc && fs.existsSync(path.join(DIR, "ghost_touch_inhibit.c"))) {
    console.log("    Building touch input inhibitor...");
    run("gcc -O2 -o ghost-touch-inhibit ghost_touch_inhibit.c -Wall");
    if (fs.existsSync(path.join(DIR, "ghost-touch-inhibit"))) {
      try {
        fs.chmodSync(path.join(DIR, "ghost-touch-inhibit"), 0o755);
      } catch {}
    }
  }

  try {
    fs.chmodSync(path.join(DIR, "ghost_screen.py"), 0o755);
  } catch {}

  console.log("  Install complete!");
  console.log('  Run: npx ghost-screen');
  if (!isGlobal) {
    console.log('  Or install globally: npm install -g ghost-screen');
  }
}

module.exports = { postinstall };

if (require.main === module) {
  postinstall();
}
