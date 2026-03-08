# 🎙️ VoiceSafeClaw v1.0

> **The fully local, secure Jarvis for Mac & Windows** — controls your entire computer by voice, zero cloud, zero cost after purchase.

---

## ✨ Features

- **🔊 Custom Wake Word** — "Hey Jarvis" (powered by openWakeWord, fully local)
- **🗣️ Local Speech-to-Text** — Whisper-tiny via faster-whisper
- **🔈 Local Text-to-Speech** — Piper-TTS / Kokoro-ONNX
- **🖥️ Full System Control** — Open apps, manage files, browser automation, shell commands
- **🛡️ SafeClaw Sandbox** — Every action requires explicit approval, no prompt injection
- **📡 Zero Cloud** — Works offline forever, no data leaves your machine
- **🖼️ Native Desktop App** — Tauri 2.0 tray/menu-bar with Vue 3 settings UI

## 📐 Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Microphone  │────▶│  Voice Loop  │────▶│   SafeClaw   │
│  (PyAudio)   │     │  wake→STT→   │     │   Engine     │
└──────────────┘     │  dispatch    │     │  sandbox +   │
                     └──────────────┘     │  executor    │
                            │             └──────┬───────┘
                            ▼                    │
                     ┌──────────────┐            ▼
                     │     TTS      │     ┌──────────────┐
                     │   Response   │◀────│   Skills     │
                     └──────────────┘     │  (10 built-  │
                                          │   in actions)│
                                          └──────────────┘
```

## 🚀 Quick Start

```bash
# 1. Clone & install
git clone https://github.com/yourorg/voicesafeclaw.git
cd voicesafeclaw
python -m venv .venv && source .venv/bin/activate
pip install -e ".[macos,dev]"   # or [windows,dev] on Windows

# 2. Copy environment config
cp .env.example .env

# 3. Run the voice assistant
python -m core.engine

# 4. Run tests
pytest tests/ -v
```

## 📁 Project Structure

```
voicesafeclaw/
├── core/           # SafeClaw engine, executor, dispatcher, sandbox
├── voice/          # Wake word, STT, TTS, voice loop
├── skills/         # 10 pre-built voice skills
├── tauri/          # Desktop app (Tauri 2.0 + Vue 3)
├── tests/          # Unit, integration, security tests
├── build/          # Output installers (.dmg, .exe)
├── requirements.txt
├── pyproject.toml
├── README.md
└── .env.example
```

## 🔒 Security Model

1. **Sandbox-first** — All actions execute inside SafeClaw sandbox
2. **Approval prompts** — Dangerous actions (file write, shell, browser) require explicit user approval
3. **No internet** — Zero network access by default
4. **No LLM injection** — Intent matching is rule-based, not prompt-based

## 🖥️ System Requirements

|                | Minimum                 |
| -------------- | ----------------------- |
| **OS**         | macOS 13+ / Windows 10+ |
| **Python**     | 3.12+                   |
| **RAM**        | 450 MB idle             |
| **Microphone** | Required                |

## 📄 License

Proprietary — see LICENSE for details.
