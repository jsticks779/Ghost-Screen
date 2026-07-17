#!/usr/bin/env node
const { execSync } = require("child_process");
const fs = require("fs");
const path = require("path");

const DIR = __dirname;

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
    __dirname.includes("/usr/lib/node_modules");

  // Check display server
  const sessionType = process.env.XDG_SESSION_TYPE || "x11";

  // Build Wayland shortcut inhibitor (.so)
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

  // Build touch inhibitor
  if (hasGcc && fs.existsSync(path.join(DIR, "ghost_touch_inhibit.c"))) {
    console.log("    Building touch input inhibitor...");
    run("gcc -O2 -o ghost-touch-inhibit ghost_touch_inhibit.c -Wall");
    if (fs.existsSync(path.join(DIR, "ghost-touch-inhibit"))) {
      try {
        fs.chmodSync(path.join(DIR, "ghost-touch-inhibit"), 0o755);
      } catch {}
    }
  }

  // Ensure ghost_screen.py is executable
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
