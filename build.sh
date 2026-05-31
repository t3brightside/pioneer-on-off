#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "🚀 Starting Nuitka build process..."

mkdir -p bin

# --- Detect OS Distribution and Architecture ---
ARCH=$(uname -m)

if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO=$ID
else
    DISTRO="linux"
fi

echo "🔍 Detected Platform: $DISTRO on $ARCH"

# --- Check for Nuitka ---
if ! command -v nuitka3 &> /dev/null && ! python3 -m nuitka --version &> /dev/null; then
    echo "❌ Error: Nuitka is not installed. Run: pip install -r requirements.txt"
    exit 1
fi

if command -v nuitka3 &> /dev/null; then
    NUITKA_CMD="nuitka3"
else
    NUITKA_CMD="python3 -m nuitka"
fi

# --- Compilation ---
FLAGS="--onefile --remove-output --output-dir=bin"

# Dynamically construct the file name with the new prefix
SERVICE_OUT="pioneer-on-off_${DISTRO}_${ARCH}.bin"

echo "⚙️ Compiling service.py into $SERVICE_OUT..."
$NUITKA_CMD $FLAGS --output-filename="$SERVICE_OUT" service.py

echo "🎉 Build complete! Your standalone binary '$SERVICE_OUT' is waiting in the 'bin/' directory."