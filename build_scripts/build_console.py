"""
Build script for creating Windows console version (with visible terminal)
Useful for debugging
"""

import os
import sys
from pathlib import Path
import PyInstaller.__main__

PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJECT_ROOT / "src"
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"
STATIC_DIR = SRC_DIR / "trackerspotter" / "static"


def build_console_exe():
    """Build console version for debugging"""
    print("🔨 Building TrackerSpotter (Console Version)...")
    
    args = [
        str(PROJECT_ROOT / "trackerspotter.py"),
        "--name", "TrackerSpotter_Console",
        "--onefile",
        "--console",  # Keep console window visible
        "--clean",
        f"--distpath={DIST_DIR}",
        f"--workpath={BUILD_DIR}",
        f"--add-data={STATIC_DIR}{os.pathsep}trackerspotter/static",
        "--hidden-import=flask",
        "--hidden-import=flask_socketio",
        "--hidden-import=socketio",
        "--hidden-import=engineio",
        "--hidden-import=bencodepy",
        "--hidden-import=simple_websocket",
    ]
    
    try:
        PyInstaller.__main__.run(args)
        print(f"\n✅ Console build successful!")
        print(f"📦 Executable: {DIST_DIR / 'TrackerSpotter_Console.exe'}")
        print(f"\n💡 This version shows the console for debugging")
        return True
    except Exception as e:
        print(f"\n❌ Build failed: {e}")
        return False


if __name__ == '__main__':
    build_console_exe()

