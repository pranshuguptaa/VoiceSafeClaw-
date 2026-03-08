#!/usr/bin/env bash
# build.sh — Full build pipeline for VoiceSafeClaw (macOS)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BUILD_DIR="$ROOT/build"
TAURI_DIR="$ROOT/tauri"

echo "=== VoiceSafeClaw Build ==="
echo "Root: $ROOT"

# Step 1: Python engine → sidecar binary
echo ""
echo "▶ [1/3] Building Python engine sidecar..."
cd "$ROOT"
python -m PyInstaller \
    --distpath "$BUILD_DIR/dist" \
    --workpath "$BUILD_DIR/work" \
    --clean \
    "$BUILD_DIR/voicesafeclaw.spec"

# Copy sidecar to Tauri binaries dir
SIDECAR_SRC="$BUILD_DIR/dist/voicesafeclaw-engine"
TAURI_BIN="$TAURI_DIR/src-tauri/binaries"
mkdir -p "$TAURI_BIN"

# Determine target triple
ARCH=$(uname -m)
case "$ARCH" in
    x86_64)  TRIPLE="x86_64-apple-darwin" ;;
    arm64)   TRIPLE="aarch64-apple-darwin" ;;
    *)       TRIPLE="$ARCH-apple-darwin" ;;
esac

cp "$SIDECAR_SRC" "$TAURI_BIN/voicesafeclaw-engine-$TRIPLE"
echo "   Sidecar copied to: $TAURI_BIN/voicesafeclaw-engine-$TRIPLE"

# Step 2: Frontend build
echo ""
echo "▶ [2/3] Building Vue frontend..."
cd "$TAURI_DIR/frontend"
npm ci
npm run build
echo "   Frontend built to: $TAURI_DIR/frontend/dist"

# Step 3: Tauri bundle
echo ""
echo "▶ [3/3] Building Tauri app bundle..."
cd "$TAURI_DIR/src-tauri"
cargo tauri build
echo ""
echo "=== Build Complete ==="
echo "Output: $TAURI_DIR/src-tauri/target/release/bundle/"
ls -la "$TAURI_DIR/src-tauri/target/release/bundle/" 2>/dev/null || echo "(check target/release/bundle for .dmg)"
