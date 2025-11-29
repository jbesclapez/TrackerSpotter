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
    print("Building TrackerSpotter (Console Version)...")
    
    args = [
        str(PROJECT_ROOT / "trackerspotter.py"),
        "--name", "TrackerSpotter_Console",
        "--onefile",
        "--console",  # Keep console window visible
        "--clean",
        f"--distpath={DIST_DIR}",
        f"--workpath={BUILD_DIR}",
        f"--add-data={STATIC_DIR}{os.pathsep}trackerspotter/static",
        
        # Core dependencies
        "--hidden-import=flask",
        "--hidden-import=bencodepy",
        
        # Flask-SocketIO and dependencies
        "--hidden-import=flask_socketio",
        "--hidden-import=socketio",
        "--hidden-import=socketio.server",
        "--hidden-import=engineio",
        "--hidden-import=engineio.server",
        "--hidden-import=engineio.async_drivers.threading",
        
        # WebSocket support
        "--hidden-import=simple_websocket",
        "--hidden-import=wsproto",
        "--hidden-import=wsproto.connection",
        "--hidden-import=wsproto.events",
        "--hidden-import=h11",
    ]
    
    try:
        PyInstaller.__main__.run(args)
        print(f"\n[SUCCESS] Console build successful!")
        print(f"Executable: {DIST_DIR / 'TrackerSpotter_Console.exe'}")
        print(f"\nNote: This version shows the console for debugging")
        return True
    except Exception as e:
        print(f"\n[ERROR] Build failed: {e}")
        return False


if __name__ == '__main__':
    build_console_exe()

