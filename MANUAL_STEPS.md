# VoiceSafeClaw — Manual Steps & Build Instructions

## Prerequisites

### macOS

```bash
# Xcode Command Line Tools
xcode-select --install

# Rust (required for Tauri)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Node.js 20+ (via Homebrew)
brew install node

# Python 3.12+
brew install python@3.12

# PortAudio (required by PyAudio for microphone)
brew install portaudio
```

### Windows

```powershell
# Install Rust from https://rustup.rs
# Install Node.js 20+ from https://nodejs.org
# Install Python 3.12+ from https://python.org
# Install Visual Studio Build Tools (for Tauri)
winget install Microsoft.VisualStudio.2022.BuildTools
```

---

## Build Commands (Mac)

```bash
cd voicesafeclaw

# 1. Python environment
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[macos,dev]"

# 2. Run tests (verify everything works)
PYTHONPATH=. pytest tests/ -v

# 3. Build the full app
chmod +x build/build.sh
./build/build.sh

# Output: tauri/src-tauri/target/release/bundle/dmg/VoiceSafeClaw_1.0.0_*.dmg
```

## Build Commands (Windows)

```powershell
cd voicesafeclaw

# 1. Python environment
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[windows,dev]"

# 2. Run tests
$env:PYTHONPATH="."
pytest tests/ -v

# 3. Build
build\build.bat

# Output: tauri\src-tauri\target\release\bundle\nsis\VoiceSafeClaw_1.0.0_*.exe
```

---

## Manual Steps (Cannot Be Automated)

### 1. macOS Microphone Permission

After first launch, macOS will prompt:

> "VoiceSafeClaw would like to access the microphone"

Click **Allow**. If missed, go to:
**System Settings → Privacy & Security → Microphone → Enable VoiceSafeClaw**

### 2. macOS Accessibility Permission (for Dictation)

For auto-typing (dictation skill), grant Accessibility:
**System Settings → Privacy & Security → Accessibility → Add VoiceSafeClaw**

### 3. macOS Code Signing & Notarization

```bash
# Sign the app
codesign --force --deep --sign "Developer ID Application: YOUR_NAME (TEAM_ID)" \
    tauri/src-tauri/target/release/bundle/macos/VoiceSafeClaw.app

# Create entitlements (already included as Entitlements.plist)
codesign --entitlements tauri/src-tauri/Entitlements.plist \
    --force --deep --sign "Developer ID Application: YOUR_NAME (TEAM_ID)" \
    tauri/src-tauri/target/release/bundle/macos/VoiceSafeClaw.app

# Notarize
xcrun notarytool submit \
    tauri/src-tauri/target/release/bundle/dmg/VoiceSafeClaw_1.0.0_*.dmg \
    --apple-id YOUR_APPLE_ID \
    --team-id YOUR_TEAM_ID \
    --password YOUR_APP_SPECIFIC_PASSWORD \
    --wait

# Staple
xcrun stapler staple \
    tauri/src-tauri/target/release/bundle/dmg/VoiceSafeClaw_1.0.0_*.dmg
```

### 4. Windows Code Signing

```powershell
# Using signtool (from Windows SDK)
signtool sign /f your-certificate.pfx /p YOUR_PASSWORD /tr http://timestamp.digicert.com /td sha256 /fd sha256 \
    tauri\src-tauri\target\release\bundle\nsis\VoiceSafeClaw_1.0.0_*.exe
```

### 5. Gumroad Upload

1. Go to [gumroad.com/products/new](https://gumroad.com/products/new)
2. Upload the `.dmg` and `.exe` installers
3. Set pricing: **$29 Early Bird (lifetime)** / **$9/mo Pro**
4. Use thumbnail text and demo script from `DEMO_SCRIPT.md`
5. Publish and share link

### 6. Download Voice Models (First Run)

On first launch, VoiceSafeClaw will auto-download:

- **openWakeWord** model (~5 MB) — "hey_jarvis" wake word
- **Whisper tiny** (~75 MB) — speech-to-text model

If you want to pre-bundle them:

```bash
# Download wake word models
python -c "import openwakeword; openwakeword.utils.download_models()"

# Download whisper model
python -c "from faster_whisper import WhisperModel; WhisperModel('tiny')"
```

### 7. Optional: Install Piper TTS Voice

```bash
# Download a Piper voice model
pip install piper-tts
# Models are downloaded automatically on first TTS call
# Or pre-download: https://github.com/rhasspy/piper/releases
```
