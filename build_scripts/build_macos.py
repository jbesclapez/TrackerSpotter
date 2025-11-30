"""
Build script for creating macOS application bundle using PyInstaller
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
BUNDLE_ID = "com.trackerspotter.app"
ICON_FILE = ICONS_DIR / "trackerspotter.icns" if (ICONS_DIR / "trackerspotter.icns").exists() else None


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


def build_app_bundle():
    """Build the macOS application bundle using PyInstaller"""
    print(f"\nBuilding {APP_NAME} v{VERSION} for macOS...")
    
    # PyInstaller arguments for macOS
    args = [
        str(PROJECT_ROOT / "trackerspotter.py"),  # Entry point
        "--name", APP_NAME,
        "--onefile",  # Single executable (inside .app bundle)
        "--windowed",  # Create .app bundle (no terminal window)
        "--clean",
        f"--distpath={DIST_DIR}",
        f"--workpath={BUILD_DIR}",
        
        # Add data files (static folder)
        f"--add-data={STATIC_DIR}:trackerspotter/static",
        
        # macOS specific
        f"--osx-bundle-identifier={BUNDLE_ID}",
        
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
    
    # Add icon if available
    if ICON_FILE and ICON_FILE.exists():
        args.extend(["--icon", str(ICON_FILE)])
        print(f"   Using icon: {ICON_FILE}")
    else:
        print("   [INFO] No .icns icon found, using default")
    
    # Run PyInstaller
    try:
        PyInstaller.__main__.run(args)
        print(f"\n[SUCCESS] Build successful!")
        print(f"App bundle location: {DIST_DIR / APP_NAME}.app")
        return True
    except Exception as e:
        print(f"\n[ERROR] Build failed: {e}")
        return False


def create_distribution_package():
    """Create a distribution package with README and other files"""
    print("\nCreating distribution package...")
    
    # Create distribution directory
    dist_package = DIST_DIR / f"{APP_NAME}_macOS"
    dist_package.mkdir(exist_ok=True)
    
    # Copy app bundle
    app_src = DIST_DIR / f"{APP_NAME}.app"
    app_dst = dist_package / f"{APP_NAME}.app"
    if app_src.exists():
        if app_dst.exists():
            shutil.rmtree(app_dst)
        shutil.copytree(app_src, app_dst)
        print(f"   [OK] Copied: {APP_NAME}.app")
    
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
    
    print(f"\n[SUCCESS] Distribution package ready: {dist_package}")
    
    # Create ZIP archive
    try:
        archive_name = f"{APP_NAME}_macOS"
        archive_path = shutil.make_archive(
            str(DIST_DIR / archive_name),
            'zip',
            dist_package
        )
        print(f"ZIP archive created: {archive_path}")
    except Exception as e:
        print(f"[WARNING] Failed to create ZIP: {e}")
    
    # Also create DMG if hdiutil is available (macOS only)
    try:
        import subprocess
        dmg_path = DIST_DIR / f"{APP_NAME}_macOS.dmg"
        
        # Remove existing DMG
        if dmg_path.exists():
            dmg_path.unlink()
        
        # Create DMG
        subprocess.run([
            'hdiutil', 'create',
            '-volname', APP_NAME,
            '-srcfolder', str(dist_package),
            '-ov',
            '-format', 'UDZO',
            str(dmg_path)
        ], check=True)
        print(f"DMG created: {dmg_path}")
    except FileNotFoundError:
        print("[INFO] hdiutil not found, skipping DMG creation")
    except subprocess.CalledProcessError as e:
        print(f"[WARNING] Failed to create DMG: {e}")
    except Exception as e:
        print(f"[WARNING] Failed to create DMG: {e}")


def verify_dependencies():
    """Verify all required packages are installed"""
    print("Verifying dependencies...")
    
    required_packages = [
        ("flask", "flask"),
        ("flask_socketio", "flask_socketio"),
        ("bencodepy", "bencodepy"),
        ("pystray", "pystray"),
        ("PIL", "Pillow"),
        ("PyInstaller", "pyinstaller"),
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
    print("""
=============================================================
          TrackerSpotter Build Script
          Creating macOS Application Bundle
=============================================================
""")
    
    # Check platform
    if sys.platform != 'darwin':
        print("[WARNING] This script is designed for macOS.")
        print("         Cross-compilation may not work correctly.")
        response = input("Continue anyway? [y/N]: ")
        if response.lower() != 'y':
            sys.exit(0)
    
    # Verify dependencies
    if not verify_dependencies():
        sys.exit(1)
    
    # Clean old builds
    clean_build_directories()
    
    # Build app bundle
    if not build_app_bundle():
        sys.exit(1)
    
    # Create distribution package
    create_distribution_package()
    
    print(f"""
=============================================================
                  BUILD COMPLETE!
=============================================================

Your macOS app bundle is ready to distribute!

To test:
  1. Go to: dist/{APP_NAME}_v{VERSION}_macOS/
  2. Double-click {APP_NAME}.app
  3. If blocked, right-click -> Open -> Open

To distribute:
  - Share the DMG file: dist/{APP_NAME}_v{VERSION}_macOS.dmg
  - Or share the ZIP: dist/{APP_NAME}_v{VERSION}_macOS.zip

Note: The app is not code-signed. Users may need to allow it
in System Preferences -> Security & Privacy.

Happy tracking!
""")


if __name__ == '__main__':
    main()

