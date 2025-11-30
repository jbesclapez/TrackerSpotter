"""
Icon generation script for TrackerSpotter
Creates icons for all platforms: PNG (Linux), ICO (Windows), ICNS (macOS)
"""

import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ImportError:
    print("ERROR: Pillow is required. Install with: pip install Pillow")
    sys.exit(1)

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
ICONS_DIR = PROJECT_ROOT / "icons"

# Icon sizes needed for each platform
WINDOWS_SIZES = [16, 24, 32, 48, 64, 128, 256]
MACOS_SIZES = [16, 32, 64, 128, 256, 512, 1024]
LINUX_SIZES = [16, 24, 32, 48, 64, 128, 256, 512]

# Color scheme (matching the app's primary color)
PRIMARY_COLOR = '#2563eb'  # Blue
SECONDARY_COLOR = '#1e40af'  # Darker blue
BACKGROUND_COLOR = (255, 255, 255, 0)  # Transparent


def hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def create_icon_image(size: int, primary_color: str = PRIMARY_COLOR) -> Image.Image:
    """
    Create a TrackerSpotter icon (target/crosshair design)
    
    Args:
        size: Icon size in pixels
        primary_color: Primary color (hex)
        
    Returns:
        PIL Image object
    """
    # Create transparent background
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Parse colors
    r, g, b = hex_to_rgb(primary_color)
    fill_color = (r, g, b, 255)
    
    # Calculate dimensions
    center = size // 2
    
    # Outer ring
    outer_margin = max(1, size // 8)
    outer_width = max(1, size // 10)
    
    # Draw outer circle (ring)
    draw.ellipse(
        [outer_margin, outer_margin, size - outer_margin, size - outer_margin],
        outline=fill_color,
        width=outer_width
    )
    
    # Inner filled circle
    inner_radius = size // 6
    draw.ellipse(
        [center - inner_radius, center - inner_radius, 
         center + inner_radius, center + inner_radius],
        fill=fill_color
    )
    
    # Crosshairs
    line_width = max(1, size // 16)
    
    # Horizontal line (left part)
    draw.rectangle(
        [outer_margin // 2, center - line_width // 2,
         center - inner_radius - line_width, center + line_width // 2],
        fill=fill_color
    )
    
    # Horizontal line (right part)
    draw.rectangle(
        [center + inner_radius + line_width, center - line_width // 2,
         size - outer_margin // 2, center + line_width // 2],
        fill=fill_color
    )
    
    # Vertical line (top part)
    draw.rectangle(
        [center - line_width // 2, outer_margin // 2,
         center + line_width // 2, center - inner_radius - line_width],
        fill=fill_color
    )
    
    # Vertical line (bottom part)
    draw.rectangle(
        [center - line_width // 2, center + inner_radius + line_width,
         center + line_width // 2, size - outer_margin // 2],
        fill=fill_color
    )
    
    return image


def create_png_icons():
    """Create PNG icons for Linux"""
    print("\nCreating PNG icons for Linux...")
    
    for size in LINUX_SIZES:
        icon = create_icon_image(size)
        output_path = ICONS_DIR / f"trackerspotter_{size}x{size}.png"
        icon.save(output_path, 'PNG')
        print(f"   [OK] Created: {output_path.name}")
    
    # Create main icon (256x256)
    main_icon = create_icon_image(256)
    main_path = ICONS_DIR / "trackerspotter.png"
    main_icon.save(main_path, 'PNG')
    print(f"   [OK] Created: trackerspotter.png (main)")
    
    return main_path


def create_ico_icon():
    """Create ICO icon for Windows"""
    print("\nCreating ICO icon for Windows...")
    
    # Create images for all sizes
    images = []
    for size in WINDOWS_SIZES:
        icon = create_icon_image(size)
        images.append(icon)
    
    # Save as ICO with multiple sizes
    output_path = ICONS_DIR / "trackerspotter.ico"
    
    # PIL can save multiple sizes in ICO format
    # We save the largest first, then include smaller sizes
    images[0].save(
        output_path,
        format='ICO',
        sizes=[(s, s) for s in WINDOWS_SIZES],
        append_images=images[1:]
    )
    
    print(f"   [OK] Created: {output_path.name}")
    return output_path


def create_icns_icon():
    """Create ICNS icon for macOS"""
    print("\nCreating ICNS icon for macOS...")
    
    # Create iconset directory
    iconset_dir = ICONS_DIR / "trackerspotter.iconset"
    iconset_dir.mkdir(exist_ok=True)
    
    # macOS iconset requires specific filenames
    iconset_sizes = [
        (16, "icon_16x16.png"),
        (32, "icon_16x16@2x.png"),
        (32, "icon_32x32.png"),
        (64, "icon_32x32@2x.png"),
        (128, "icon_128x128.png"),
        (256, "icon_128x128@2x.png"),
        (256, "icon_256x256.png"),
        (512, "icon_256x256@2x.png"),
        (512, "icon_512x512.png"),
        (1024, "icon_512x512@2x.png"),
    ]
    
    for size, filename in iconset_sizes:
        icon = create_icon_image(size)
        icon_path = iconset_dir / filename
        icon.save(icon_path, 'PNG')
        print(f"   [OK] Created: {filename}")
    
    # Try to convert to ICNS using iconutil (macOS only)
    output_path = ICONS_DIR / "trackerspotter.icns"
    
    try:
        import subprocess
        subprocess.run([
            'iconutil',
            '-c', 'icns',
            str(iconset_dir),
            '-o', str(output_path)
        ], check=True)
        print(f"   [OK] Created: {output_path.name}")
        
        # Clean up iconset directory
        import shutil
        shutil.rmtree(iconset_dir)
        print("   [OK] Cleaned up iconset directory")
        
    except FileNotFoundError:
        print(f"   [INFO] iconutil not found (not on macOS)")
        print(f"   [INFO] Iconset created at: {iconset_dir}")
        print(f"   [INFO] To create .icns, run on macOS: iconutil -c icns {iconset_dir}")
        
        # Create a basic ICNS-like file using Pillow (limited support)
        # This won't be a proper ICNS but can serve as placeholder
        try:
            largest = create_icon_image(512)
            largest.save(output_path, 'PNG')  # Save as PNG with .icns extension as fallback
            print(f"   [INFO] Created placeholder: {output_path.name} (convert on macOS)")
        except Exception:
            pass
    
    except subprocess.CalledProcessError as e:
        print(f"   [WARNING] Failed to create ICNS: {e}")
    
    return output_path


def create_favicon():
    """Create favicon for web UI"""
    print("\nCreating favicon for web UI...")
    
    # Create 32x32 favicon
    icon = create_icon_image(32)
    output_path = ICONS_DIR / "favicon.ico"
    icon.save(output_path, 'ICO')
    print(f"   [OK] Created: {output_path.name}")
    
    # Also create PNG version
    png_path = ICONS_DIR / "favicon.png"
    icon.save(png_path, 'PNG')
    print(f"   [OK] Created: {png_path.name}")
    
    return output_path


def main():
    """Generate all icons"""
    print("""
=============================================================
          TrackerSpotter Icon Generator
=============================================================
""")
    
    # Create icons directory
    ICONS_DIR.mkdir(exist_ok=True)
    print(f"Icons directory: {ICONS_DIR}")
    
    # Generate icons for each platform
    create_png_icons()
    create_ico_icon()
    create_icns_icon()
    create_favicon()
    
    print("""
=============================================================
                  ICONS GENERATED!
=============================================================

Created icons:
  - trackerspotter.png     (Linux, 256x256)
  - trackerspotter.ico     (Windows, multi-size)
  - trackerspotter.icns    (macOS, or .iconset folder)
  - favicon.ico/png        (Web UI)
  - Various sized PNGs     (For high-DPI displays)

To use in builds:
  - Windows: icons/trackerspotter.ico
  - macOS:   icons/trackerspotter.icns
  - Linux:   icons/trackerspotter.png

Note: For proper macOS ICNS, run this script on macOS
where iconutil is available.
""")


if __name__ == '__main__':
    main()

