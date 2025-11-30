"""
System Tray Icon for TrackerSpotter
Provides visual indication that the server is running and quick access to controls.
"""

import threading
import webbrowser
import sys
import subprocess
from typing import Callable, Optional

try:
    import pystray
    from PIL import Image, ImageDraw
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False


def copy_to_clipboard(text: str) -> bool:
    """
    Cross-platform clipboard copy function.
    
    Args:
        text: Text to copy to clipboard
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if sys.platform == 'win32':
            # Windows: use clip.exe
            process = subprocess.Popen(
                ['clip.exe'],
                stdin=subprocess.PIPE,
                shell=True
            )
            process.communicate(text.encode('utf-8'))
            return True
        elif sys.platform == 'darwin':
            # macOS: use pbcopy
            process = subprocess.Popen(
                ['pbcopy'],
                stdin=subprocess.PIPE
            )
            process.communicate(text.encode('utf-8'))
            return True
        else:
            # Linux: try xclip, then xsel
            try:
                process = subprocess.Popen(
                    ['xclip', '-selection', 'clipboard'],
                    stdin=subprocess.PIPE
                )
                process.communicate(text.encode('utf-8'))
                return True
            except FileNotFoundError:
                try:
                    process = subprocess.Popen(
                        ['xsel', '--clipboard', '--input'],
                        stdin=subprocess.PIPE
                    )
                    process.communicate(text.encode('utf-8'))
                    return True
                except FileNotFoundError:
                    return False
    except Exception:
        return False


def create_icon_image(size: int = 64, color: str = '#2563eb') -> 'Image.Image':
    """
    Create a simple target/crosshair icon for the tray
    
    Args:
        size: Icon size in pixels
        color: Primary color (hex)
        
    Returns:
        PIL Image object
    """
    # Create a simple target icon
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Parse hex color
    r = int(color[1:3], 16)
    g = int(color[3:5], 16)
    b = int(color[5:7], 16)
    fill_color = (r, g, b, 255)
    
    # Draw outer circle
    margin = size // 8
    draw.ellipse(
        [margin, margin, size - margin, size - margin],
        outline=fill_color,
        width=size // 12
    )
    
    # Draw inner circle
    inner_margin = size // 3
    draw.ellipse(
        [inner_margin, inner_margin, size - inner_margin, size - inner_margin],
        fill=fill_color
    )
    
    # Draw crosshairs
    center = size // 2
    line_width = size // 16
    # Horizontal line
    draw.rectangle(
        [0, center - line_width, size, center + line_width],
        fill=fill_color
    )
    # Vertical line
    draw.rectangle(
        [center - line_width, 0, center + line_width, size],
        fill=fill_color
    )
    
    return image


class TrayIcon:
    """System tray icon manager for TrackerSpotter"""
    
    def __init__(
        self,
        host: str,
        port: int,
        on_exit: Optional[Callable] = None
    ):
        """
        Initialize tray icon
        
        Args:
            host: Server host address
            port: Server port
            on_exit: Callback function when exit is requested
        """
        self.host = host
        self.port = port
        self.on_exit = on_exit
        self.icon: Optional['pystray.Icon'] = None
        self._thread: Optional[threading.Thread] = None
        
        # Determine display host (show 127.0.0.1 if bound to 0.0.0.0)
        self.display_host = '127.0.0.1' if host == '0.0.0.0' else host
        
    @property
    def dashboard_url(self) -> str:
        """Get the dashboard URL"""
        return f"http://{self.display_host}:{self.port}"
    
    @property
    def tracker_url(self) -> str:
        """Get the tracker announce URL"""
        return f"http://{self.display_host}:{self.port}/announce"
    
    def _create_menu(self) -> 'pystray.Menu':
        """Create the context menu"""
        return pystray.Menu(
            pystray.MenuItem(
                f"TrackerSpotter - {self.display_host}:{self.port}",
                None,
                enabled=False
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "Open Dashboard",
                self._open_dashboard,
                default=True  # Double-click action
            ),
            pystray.MenuItem(
                "Copy HTTP Tracker URL",
                self._copy_http_url
            ),
            pystray.MenuItem(
                "Copy UDP Tracker URL",
                self._copy_udp_url
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "Exit",
                self._exit_app
            )
        )
    
    def _open_dashboard(self, icon=None, item=None):
        """Open dashboard in browser"""
        try:
            webbrowser.open(self.dashboard_url)
        except Exception:
            pass
    
    def _copy_http_url(self, icon=None, item=None):
        """Copy HTTP tracker URL to clipboard"""
        url = f"http://{self.display_host}:{self.port}/announce"
        copy_to_clipboard(url)
    
    def _copy_udp_url(self, icon=None, item=None):
        """Copy UDP tracker URL to clipboard"""
        url = f"udp://{self.display_host}:{self.port}/announce"
        copy_to_clipboard(url)
    
    def _exit_app(self, icon=None, item=None):
        """Exit the application"""
        if self.icon:
            self.icon.stop()
        if self.on_exit:
            self.on_exit()
        else:
            sys.exit(0)
    
    def start(self):
        """Start the tray icon in a background thread"""
        if not TRAY_AVAILABLE:
            return
        
        def run_tray():
            try:
                image = create_icon_image()
                tooltip = f"TrackerSpotter\nRunning on {self.display_host}:{self.port}"
                
                self.icon = pystray.Icon(
                    "TrackerSpotter",
                    image,
                    tooltip,
                    menu=self._create_menu()
                )
                self.icon.run()
            except Exception as e:
                # Silently fail if tray icon can't be created
                print(f"Note: System tray icon not available ({e})")
        
        self._thread = threading.Thread(target=run_tray, daemon=True)
        self._thread.start()
    
    def stop(self):
        """Stop the tray icon"""
        if self.icon:
            try:
                self.icon.stop()
            except Exception:
                pass


def is_tray_available() -> bool:
    """Check if system tray is available"""
    return TRAY_AVAILABLE

