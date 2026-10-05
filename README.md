# Mythral Lens — desktop app

**Mythral Lens** by MythralCreations: cinematic 3D renders of Minecraft builds
(`.schematic`, `.schem`, `.litematic`, `.nbt`). This repository builds a fully
offline Windows app with GitHub Actions — nothing to install on your own PC.

## What you get
- `Mythral Lens.msi` – installer: Start Menu entry, desktop shortcut, uninstall from Windows settings.
- `Mythral Lens.exe` – portable app: runs without installing.

Both work **offline**: the 3D libraries and fonts are bundled during the build.

## Build it (no coding tools needed)
1. Upload this whole folder to a new GitHub repository (see the step-by-step guide).
2. Open the **Actions** tab → **Build Mythral Lens for Windows** → **Run workflow**.
3. Wait for the green check mark (first build ~10–15 min, later ~5 min).
4. Open the finished run → **Artifacts** → download **Mythral-Lens-Windows** and unzip it.

Every time you update `app/index.html`, the build runs again automatically.

## Project layout
| Path | Purpose |
| --- | --- |
| `app/index.html` | the Mythral Lens app |
| `app/icon.ico`, `app/icon.png` | app icon (MythralCreations logo) |
| `scripts/prepare_offline.py` | downloads libraries + fonts into the app so it runs offline |
| `.github/workflows/build.yml` | the Windows build (uses [Pake](https://github.com/tw93/Pake), built on Tauri) |

## Notes
- Requires Windows 10/11 (uses the built-in Microsoft Edge WebView2 runtime).
- The app is not code-signed, so Windows SmartScreen may show a warning the first time:
  click **More info → Run anyway**.
- Minecraft textures belong to Mojang and are **not** included. Each user loads their own
  game `client.jar` or the official Mojang Bedrock sample pack inside the app.
