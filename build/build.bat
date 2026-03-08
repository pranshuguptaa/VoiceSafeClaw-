@echo off
REM build.bat — Full build pipeline for VoiceSafeClaw (Windows)

set ROOT=%~dp0..
set BUILD_DIR=%ROOT%\build
set TAURI_DIR=%ROOT%\tauri

echo === VoiceSafeClaw Build (Windows) ===

REM Step 1: Python engine sidecar
echo.
echo [1/3] Building Python engine sidecar...
cd /d "%ROOT%"
python -m PyInstaller ^
    --distpath "%BUILD_DIR%\dist" ^
    --workpath "%BUILD_DIR%\work" ^
    --clean ^
    "%BUILD_DIR%\voicesafeclaw.spec"

REM Copy sidecar to Tauri binaries
set TAURI_BIN=%TAURI_DIR%\src-tauri\binaries
if not exist "%TAURI_BIN%" mkdir "%TAURI_BIN%"
copy "%BUILD_DIR%\dist\voicesafeclaw-engine.exe" "%TAURI_BIN%\voicesafeclaw-engine-x86_64-pc-windows-msvc.exe"
echo    Sidecar copied.

REM Step 2: Frontend
echo.
echo [2/3] Building Vue frontend...
cd /d "%TAURI_DIR%\frontend"
call npm ci
call npm run build

REM Step 3: Tauri bundle
echo.
echo [3/3] Building Tauri app...
cd /d "%TAURI_DIR%\src-tauri"
cargo tauri build

echo.
echo === Build Complete ===
echo Check: %TAURI_DIR%\src-tauri\target\release\bundle\
