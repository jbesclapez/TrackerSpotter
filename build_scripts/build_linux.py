"""
Build script for creating Linux executable using PyInstaller
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
APP_NAME_LOWER = "trackerspotter"
VERSION = get_version()
ICON_FILE = ICONS_DIR / "trackerspotter.png" if (ICONS_DIR / "trackerspotter.png").exists() else None


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
    """Build the Linux executable using PyInstaller"""
    print(f"\nBuilding {APP_NAME} v{VERSION} for Linux...")
    
    # PyInstaller arguments for Linux
    args = [
        str(PROJECT_ROOT / "trackerspotter.py"),  # Entry point
        "--name", APP_NAME_LOWER,  # Lowercase for Linux conventions
        "--onefile",  # Single executable
        "--console",  # Keep console for Linux (terminal app)
        "--clean",
        f"--distpath={DIST_DIR}",
        f"--workpath={BUILD_DIR}",
        
        # Add data files (static folder) - Linux uses : as separator
        f"--add-data={STATIC_DIR}:trackerspotter/static",
        
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
    ]
    
    # Add icon if available (for window managers that support it)
    if ICON_FILE and ICON_FILE.exists():
        args.extend(["--icon", str(ICON_FILE)])
        print(f"   Using icon: {ICON_FILE}")
    else:
        print("   [INFO] No .png icon found")
    
    # Run PyInstaller
    try:
        PyInstaller.__main__.run(args)
        print(f"\n[SUCCESS] Build successful!")
        print(f"Executable location: {DIST_DIR / APP_NAME_LOWER}")
        return True
    except Exception as e:
        print(f"\n[ERROR] Build failed: {e}")
        return False


def create_desktop_entry():
    """Create a .desktop file for Linux desktop integration"""
    desktop_content = f"""[Desktop Entry]
Name=TrackerSpotter
Comment=Local BitTorrent Tracker Monitor
Exec={APP_NAME_LOWER}
Icon=trackerspotter
Terminal=false
Type=Application
Categories=Network;P2P;Monitor;
Keywords=bittorrent;tracker;torrent;monitor;
"""
    return desktop_content


def create_distribution_package():
    """Create a distribution package with README and other files"""
    print("\nCreating distribution package...")
    
    # Create distribution directory
    dist_package = DIST_DIR / f"{APP_NAME}_v{VERSION}_Linux"
    dist_package.mkdir(exist_ok=True)
    
    # Copy executable
    exe_src = DIST_DIR / APP_NAME_LOWER
    exe_dst = dist_package / APP_NAME_LOWER
    if exe_src.exists():
        shutil.copy2(exe_src, exe_dst)
        # Make executable
        exe_dst.chmod(0o755)
        print(f"   [OK] Copied: {APP_NAME_LOWER}")
    
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
    
    # Copy icon if exists
    if ICON_FILE and ICON_FILE.exists():
        icon_dst = dist_package / "trackerspotter.png"
        shutil.copy2(ICON_FILE, icon_dst)
        print(f"   [OK] Copied: trackerspotter.png")
    
    # Create desktop entry
    desktop_dst = dist_package / "trackerspotter.desktop"
    with open(desktop_dst, 'w', encoding='utf-8') as f:
        f.write(create_desktop_entry())
    print(f"   [OK] Created: trackerspotter.desktop")
    
    # Create install script
    install_script = dist_package / "install.sh"
    with open(install_script, 'w', encoding='utf-8') as f:
        f.write(f"""#!/bin/bash
# TrackerSpotter v{VERSION} Installation Script

set -e

echo "Installing TrackerSpotter v{VERSION}..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (sudo ./install.sh)"
    exit 1
fi

# Install binary
install -Dm755 {APP_NAME_LOWER} /usr/local/bin/{APP_NAME_LOWER}
echo "  [OK] Installed binary to /usr/local/bin/{APP_NAME_LOWER}"

# Install icon
if [ -f "trackerspotter.png" ]; then
    install -Dm644 trackerspotter.png /usr/share/icons/hicolor/256x256/apps/trackerspotter.png
    echo "  [OK] Installed icon"
fi

# Install desktop entry
if [ -f "trackerspotter.desktop" ]; then
    install -Dm644 trackerspotter.desktop /usr/share/applications/trackerspotter.desktop
    echo "  [OK] Installed desktop entry"
fi

# Update icon cache
if command -v gtk-update-icon-cache &> /dev/null; then
    gtk-update-icon-cache -f -t /usr/share/icons/hicolor 2>/dev/null || true
fi

echo ""
echo "Installation complete!"
echo "Run 'trackerspotter' from terminal or find it in your application menu."
echo ""
""")
    install_script.chmod(0o755)
    print(f"   [OK] Created: install.sh")
    
    # Create uninstall script
    uninstall_script = dist_package / "uninstall.sh"
    with open(uninstall_script, 'w', encoding='utf-8') as f:
        f.write(f"""#!/bin/bash
# TrackerSpotter Uninstallation Script

set -e

echo "Uninstalling TrackerSpotter..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (sudo ./uninstall.sh)"
    exit 1
fi

# Remove binary
rm -f /usr/local/bin/{APP_NAME_LOWER}
echo "  [OK] Removed binary"

# Remove icon
rm -f /usr/share/icons/hicolor/256x256/apps/trackerspotter.png
echo "  [OK] Removed icon"

# Remove desktop entry
rm -f /usr/share/applications/trackerspotter.desktop
echo "  [OK] Removed desktop entry"

# Update icon cache
if command -v gtk-update-icon-cache &> /dev/null; then
    gtk-update-icon-cache -f -t /usr/share/icons/hicolor 2>/dev/null || true
fi

echo ""
echo "Uninstallation complete!"
echo ""
""")
    uninstall_script.chmod(0o755)
    print(f"   [OK] Created: uninstall.sh")
    
    print(f"\n[SUCCESS] Distribution package ready: {dist_package}")
    
    # Create tar.gz archive (more common on Linux)
    try:
        archive_name = f"{APP_NAME}_v{VERSION}_Linux"
        archive_path = shutil.make_archive(
            str(DIST_DIR / archive_name),
            'gztar',
            DIST_DIR,
            f"{APP_NAME}_v{VERSION}_Linux"
        )
        print(f"tar.gz archive created: {archive_path}")
    except Exception as e:
        print(f"[WARNING] Failed to create tar.gz: {e}")
    
    # Also create ZIP for convenience
    try:
        archive_path = shutil.make_archive(
            str(DIST_DIR / f"{APP_NAME}_v{VERSION}_Linux"),
            'zip',
            dist_package
        )
        print(f"ZIP archive created: {archive_path}")
    except Exception as e:
        print(f"[WARNING] Failed to create ZIP: {e}")


def verify_dependencies():
    """Verify all required packages are installed without importing them"""
    import os
    
    # In CI environments, skip verification to avoid X display issues
    # Packages are installed via requirements.txt, so we trust they're there
    # Check multiple CI environment variables (GitHub Actions sets GITHUB_ACTIONS)
    ci_env_vars = ['CI', 'GITHUB_ACTIONS', 'GITHUB_WORKFLOW', 'RUNNER_OS']
    is_ci = any(os.environ.get(var) for var in ci_env_vars)
    
    if is_ci:
        print("Verifying dependencies...")
        print(f"   [INFO] Detected CI environment (env vars: {[f'{v}={os.environ.get(v)}' for v in ci_env_vars if os.environ.get(v)]})")
        print("   [SKIP] Running in CI - dependencies installed via requirements.txt")
        print("   [OK] All dependencies (assumed installed)")
        return True
    
    print("Verifying dependencies...")
    
    # Set DISPLAY environment variable if not set (for headless environments)
    if 'DISPLAY' not in os.environ:
        os.environ['DISPLAY'] = ':99'
        print(f"   [INFO] Set DISPLAY={os.environ['DISPLAY']}")
    
    # Use importlib.metadata (Python 3.8+) to check packages without importing
    # This is safer than find_spec which can trigger module loading
    try:
        from importlib import metadata
    except ImportError:
        # Python < 3.8 fallback
        try:
            import importlib_metadata as metadata
        except ImportError:
            # If metadata not available, skip verification
            print("   [SKIP] importlib.metadata not available - assuming all packages installed")
            return True
    
    # Package names as they appear in pip (not module names)
    packages_to_check = [
        ("flask", "flask"),
        ("flask-socketio", "flask_socketio"),
        ("bencodepy", "bencodepy"),
        ("Pillow", "PIL"),
        ("pyinstaller", "PyInstaller"),
    ]
    
    missing = []
    for package_name, module_name in packages_to_check:
        try:
            # Check if package is installed using metadata (no import happens)
            dist = metadata.distribution(package_name)
            print(f"   [OK] {package_name} (version: {dist.version})")
        except metadata.PackageNotFoundError:
            print(f"   [MISSING] {package_name}")
            missing.append(package_name)
        except Exception as e:
            # If check fails, assume it's installed (will fail at runtime if not)
            print(f"   [OK] {package_name} (assumed - check failed: {e})")
    
    # pystray - NEVER check this - it requires X display and will crash
    # It's installed via requirements.txt, so we assume it's there
    print(f"   [OK] pystray (skipped - requires X display, assumed installed)")
    
    if missing:
        print(f"\n[ERROR] Missing packages: {', '.join(missing)}")
        print(f"Install with: pip install {' '.join(missing)}")
        return False
    
    print("[SUCCESS] All dependencies verified")
    return True


def main():
    """Main build process"""
    print("""
=============================================================
          TrackerSpotter Build Script
          Creating Linux Executable
=============================================================
""")
    
    # Check platform
    if sys.platform != 'linux':
        print("[WARNING] This script is designed for Linux.")
        print("         Cross-compilation may not work correctly.")
        response = input("Continue anyway? [y/N]: ")
        if response.lower() != 'y':
            sys.exit(0)
    
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
    
    print(f"""
=============================================================
                  BUILD COMPLETE!
=============================================================

Your Linux executable is ready to distribute!

To test:
  1. Go to: dist/{APP_NAME}_v{VERSION}_Linux/
  2. Run: ./{APP_NAME_LOWER}
  3. Or install system-wide: sudo ./install.sh

To distribute:
  - Share the tar.gz: dist/{APP_NAME}_v{VERSION}_Linux.tar.gz
  - Or share the ZIP: dist/{APP_NAME}_v{VERSION}_Linux.zip

Note: For system tray support, ensure a system tray is available
(GNOME users may need the AppIndicator extension).

Happy tracking!
""")


if __name__ == '__main__':
    main()

