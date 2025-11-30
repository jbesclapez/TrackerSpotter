"""
Build script for creating Windows executable using PyInstaller
"""

import os
import sys
import re
import shutil
from pathlib import Path
import PyInstaller.__main__

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJECT_ROOT / "src"
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"
STATIC_DIR = SRC_DIR / "trackerspotter" / "static"
ICONS_DIR = PROJECT_ROOT / "icons"


def get_version():
    """Read version from __init__.py (single source of truth)"""
    init_file = SRC_DIR / "trackerspotter" / "__init__.py"
    content = init_file.read_text(encoding="utf-8")
    match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
    return match.group(1) if match else "0.0.0"


# Build configuration
APP_NAME = "TrackerSpotter"
VERSION = get_version()
ICON_FILE = ICONS_DIR / "trackerspotter.ico" if (ICONS_DIR / "trackerspotter.ico").exists() else None


def clean_build_directories():
    """Clean previous build artifacts"""
    print("Cleaning build directories...")
    
    for directory in [DIST_DIR, BUILD_DIR]:
        if directory.exists():
            try:
                shutil.rmtree(directory)
                print(f"   Removed: {directory}")
            except PermissionError as e:
                print(f"   [WARNING] Could not remove {directory}: {e}")
                print(f"   [INFO] Continuing with build (files may be locked by another process)")
            except Exception as e:
                print(f"   [WARNING] Could not remove {directory}: {e}")
    
    # Remove spec file
    spec_file = PROJECT_ROOT / f"{APP_NAME}.spec"
    if spec_file.exists():
        try:
            spec_file.unlink()
            print(f"   Removed: {spec_file}")
        except Exception as e:
            print(f"   [WARNING] Could not remove {spec_file}: {e}")


def build_executable():
    """Build the Windows executable using PyInstaller"""
    print(f"\nBuilding {APP_NAME} v{VERSION}...")
    
    # PyInstaller arguments
    args = [
        str(PROJECT_ROOT / "trackerspotter.py"),  # Entry point
        "--name", APP_NAME,
        "--onefile",  # Single executable
        "--windowed",  # No console window (GUI app)
        "--clean",
        f"--distpath={DIST_DIR}",
        f"--workpath={BUILD_DIR}",
        
        # Add data files (static folder)
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
        
        # System tray support
        "--hidden-import=pystray",
        "--hidden-import=PIL",
        "--hidden-import=PIL.Image",
        "--hidden-import=PIL.ImageDraw",
        
        # Console for debugging (remove --windowed above and uncomment this for debug builds)
        # "--console",
    ]
    
    # Add icon if available
    if ICON_FILE and ICON_FILE.exists():
        args.extend(["--icon", str(ICON_FILE)])
    
    # Run PyInstaller
    try:
        PyInstaller.__main__.run(args)
        print(f"\n[SUCCESS] Build successful!")
        print(f"Executable location: {DIST_DIR / APP_NAME}.exe")
        return True
    except Exception as e:
        print(f"\n[ERROR] Build failed: {e}")
        return False


def create_distribution_package():
    """Create a distribution package with README and other files"""
    print("\nCreating distribution package...")
    
    # Create distribution directory
    dist_package = DIST_DIR / f"{APP_NAME}_Windows"
    dist_package.mkdir(exist_ok=True)
    
    # Copy executable
    exe_src = DIST_DIR / f"{APP_NAME}.exe"
    exe_dst = dist_package / f"{APP_NAME}.exe"
    if exe_src.exists():
        shutil.copy2(exe_src, exe_dst)
        print(f"   [OK] Copied: {APP_NAME}.exe")
    
    # Copy README
    readme_src = PROJECT_ROOT / "README.md"
    readme_dst = dist_package / "README.md"
    if readme_src.exists():
        shutil.copy2(readme_src, readme_dst)
        print(f"   [OK] Copied: README.md")
    
    # Copy Usage Guide
    usage_src = PROJECT_ROOT / "docs" / "USAGE_GUIDE.md"
    usage_dst = dist_package / "USAGE_GUIDE.md"
    if usage_src.exists():
        shutil.copy2(usage_src, usage_dst)
        print(f"   [OK] Copied: USAGE_GUIDE.md")
    
    # Copy License
    license_src = PROJECT_ROOT / "LICENSE"
    license_dst = dist_package / "LICENSE.txt"
    if license_src.exists():
        shutil.copy2(license_src, license_dst)
        print(f"   [OK] Copied: LICENSE.txt")
    
    # Create quick start file
    quickstart_dst = dist_package / "QUICKSTART.txt"
    with open(quickstart_dst, 'w', encoding='utf-8') as f:
        f.write(f"""
=============================================================
              TrackerSpotter v{VERSION}
          Local BitTorrent Tracker Monitor
=============================================================

QUICK START:

1. Double-click TrackerSpotter.exe to run
   (Your browser will open automatically)

2. Copy a tracker URL from the dashboard:
   HTTP: http://127.0.0.1:6969/announce
   UDP:  udp://127.0.0.1:6969/announce (recommended)

3. Add it to your torrent client's tracker list:
   - qBittorrent: Right-click torrent -> Edit trackers
   - Transmission: Properties -> Trackers -> Add
   - Deluge: Right-click -> Edit Trackers

4. Start a torrent and watch events appear!

DOCUMENTATION:
- See README.md for detailed information
- See USAGE_GUIDE.md for step-by-step instructions

TROUBLESHOOTING:
- Port in use? Close other apps using port 6969
- No events? Check tracker URL is correct
- Need help? Visit: https://github.com/jbesclapez/TrackerSpotter

Made with love for the BitTorrent community
""")
    print(f"   [OK] Created: QUICKSTART.txt")
    
    print(f"\n[SUCCESS] Distribution package ready: {dist_package}")
    
    # Create ZIP archive
    try:
        archive_name = f"{APP_NAME}_Windows"
        archive_path = shutil.make_archive(
            str(DIST_DIR / archive_name),
            'zip',
            dist_package
        )
        print(f"ZIP archive created: {archive_path}")
    except Exception as e:
        print(f"[WARNING] Failed to create ZIP: {e}")


def verify_dependencies():
    """Verify all required packages are installed"""
    print("Verifying dependencies...")
    
    required_packages = [
        ("flask", "flask"),
        ("flask_socketio", "flask_socketio"),
        ("bencodepy", "bencodepy"),
        ("pystray", "pystray"),
        ("PIL", "Pillow"),
        ("PyInstaller", "pyinstaller"),  # Module name vs package name
    ]
    
    missing = []
    for module_name, package_name in required_packages:
        try:
            __import__(module_name)
            print(f"   [OK] {package_name}")
        except ImportError:
            print(f"   [MISSING] {package_name}")
            missing.append(package_name)
    
    if missing:
        print(f"\n[ERROR] Missing packages: {', '.join(missing)}")
        print(f"Install with: pip install {' '.join(missing)}")
        return False
    
    print("[SUCCESS] All dependencies installed")
    return True


def main():
    """Main build process"""
    import sys
    
    # Try to set UTF-8 encoding
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
    
    print("""
=============================================================
          TrackerSpotter Build Script
          Creating Windows Executable
=============================================================
""")
    
    # Verify dependencies
    if not verify_dependencies():
        sys.exit(1)
    
    # Clean old builds
    clean_build_directories()
    
    # Build executable
    if not build_executable():
        sys.exit(1)
    
    # Create distribution package
    create_distribution_package()
    
    print("""
=============================================================
                  BUILD COMPLETE!
=============================================================

Your executable is ready to distribute!

To test:
  1. Go to: dist/TrackerSpotter_v1.0.0_Windows/
  2. Double-click TrackerSpotter.exe
  3. Follow the quick start instructions

To distribute:
  - Share the ZIP file: dist/TrackerSpotter_v1.0.0_Windows.zip
  - Or share the entire folder: dist/TrackerSpotter_v1.0.0_Windows/

Happy tracking!
""")


if __name__ == '__main__':
    main()

