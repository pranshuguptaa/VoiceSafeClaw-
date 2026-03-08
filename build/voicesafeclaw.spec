# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for VoiceSafeClaw Python engine sidecar."""

import sys
from pathlib import Path

block_cipher = None
ROOT = Path(SPECPATH).parent

a = Analysis(
    [str(ROOT / "core" / "engine.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=[
        (str(ROOT / "skills"), "skills"),
        (str(ROOT / ".env.example"), "."),
    ],
    hiddenimports=[
        "core", "core.engine", "core.executor", "core.dispatcher", "core.sandbox",
        "voice", "voice.wake", "voice.stt", "voice.tts", "voice.loop",
        "skills", "skills.app_launcher", "skills.file_manager", "skills.browser",
        "skills.shell", "skills.dictation", "skills.screenshot",
        "skills.calendar_skill", "skills.email_draft", "skills.notification",
        "skills.web_search",
        "openwakeword", "faster_whisper", "piper",
        "sounddevice", "numpy", "pyaudio",
        "pyautogui", "psutil", "pyperclip",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "scipy"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="voicesafeclaw-engine",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True if sys.platform == "darwin" else False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(ROOT / "tauri" / "src-tauri" / "icons" / "icon.icns")
    if sys.platform == "darwin"
    else str(ROOT / "tauri" / "src-tauri" / "icons" / "icon.ico"),
)
