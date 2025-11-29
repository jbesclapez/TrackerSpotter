"""
TrackerSpotter - Main entry point
"""

import sys
import webbrowser
import threading
import time
import socket
import argparse
from pathlib import Path

from . import __version__
from .tracker_server import TrackerServer
from .tray import TrayIcon, is_tray_available


def open_browser(url: str, delay: float = 1.5):
    """
    Open browser after a delay
    
    Args:
        url: URL to open
        delay: Seconds to wait before opening
    """
    time.sleep(delay)
    try:
        webbrowser.open(url)
    except Exception:
        pass  # Silently fail if browser can't be opened


def find_available_port(start_port: int = 6969, max_attempts: int = 10) -> int:
    """
    Find an available port starting from start_port
    
    Args:
        start_port: Preferred port to start searching from
        max_attempts: Maximum number of ports to try
        
    Returns:
        Available port number
        
    Raises:
        OSError: If no available port found in range
    """
    for offset in range(max_attempts):
        port = start_port + offset
        try:
            # Test if port is available by attempting to bind
            # Don't use SO_REUSEADDR here - we want strict checking
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.bind(('127.0.0.1', port))
            test_socket.close()
            return port
        except OSError:
            continue
    
    raise OSError(f"No available ports found in range {start_port}-{start_port + max_attempts - 1}")


def format_url_host(host: str, is_ipv6: bool = False) -> str:
    """Format host for URL display (add brackets for IPv6)"""
    if is_ipv6 or ':' in host:
        return f"[{host}]"
    return host


def print_banner(host: str, port: int, enable_ipv6: bool = False):
    """
    Print startup banner
    
    Args:
        host: Server host
        port: Server port
        enable_ipv6: Whether IPv6 is enabled
    """
    # Try to set UTF-8 encoding for better character support
    import sys
    import io
    
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
    
    url_host = format_url_host(host)
    
    ipv6_section = ""
    if enable_ipv6:
        ipv6_host = '::1' if host == '127.0.0.1' else '::' if host == '0.0.0.0' else None
        if ipv6_host:
            ipv6_section = f"""
  IPv6 HTTP:    http://[{ipv6_host}]:{port}/announce
  IPv6 UDP:     udp://[{ipv6_host}]:{port}/announce"""
    
    banner = f"""
================================================================
                  TrackerSpotter v{__version__}
           Local BitTorrent Tracker Monitor
================================================================

  Status: Running
  
  HTTP Tracker: http://{url_host}:{port}/announce
  UDP Tracker:  udp://{url_host}:{port}/announce{ipv6_section}
  Dashboard:    http://{url_host}:{port}

  Copy a tracker URL above and add it to your torrent
  client to start monitoring announces!
  
  Tip: UDP is faster and preferred by most clients

  Press Ctrl+C to stop
================================================================
"""
    print(banner)


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='TrackerSpotter - Local BitTorrent Tracker Monitor',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  trackerspotter                    # Run on localhost:6969 (default)
  trackerspotter --port 8080        # Run on localhost:8080
  trackerspotter --host 0.0.0.0     # Expose to LAN (requires firewall config)
  trackerspotter --host 192.168.1.5 # Bind to specific interface
  trackerspotter --no-browser       # Don't auto-open browser

Security Note:
  By default, TrackerSpotter binds to 127.0.0.1 (localhost only).
  Using --host 0.0.0.0 or a LAN IP will expose the tracker to your network.
  Make sure to configure your firewall appropriately.
        """
    )
    parser.add_argument(
        '--host', '-H',
        default='127.0.0.1',
        help='Host/IP to bind to (default: 127.0.0.1). Use 0.0.0.0 for all interfaces.'
    )
    parser.add_argument(
        '--port', '-p',
        type=int,
        default=6969,
        help='Port to listen on (default: 6969)'
    )
    parser.add_argument(
        '--no-browser',
        action='store_true',
        help='Do not automatically open browser on startup'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode'
    )
    parser.add_argument(
        '--ipv6',
        action='store_true',
        help='Enable IPv6 support (binds to ::1 in addition to IPv4)'
    )
    parser.add_argument(
        '--version', '-v',
        action='version',
        version=f'TrackerSpotter {__version__}'
    )
    return parser.parse_args()


def main():
    """Main entry point for TrackerSpotter"""
    
    # Parse command line arguments
    args = parse_args()
    
    HOST = args.host
    DEBUG = args.debug
    PREFERRED_PORT = args.port
    AUTO_BROWSER = not args.no_browser
    ENABLE_IPV6 = args.ipv6
    
    # Try to set console encoding to UTF-8 for emoji support
    try:
        if sys.platform == 'win32':
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleOutputCP(65001)  # UTF-8
    except Exception:
        pass  # If it fails, we'll use ASCII symbols
    
    # Security warning for non-localhost binding
    if HOST != '127.0.0.1':
        print("\n" + "="*60)
        print("⚠️  SECURITY WARNING")
        print("="*60)
        print(f"You are binding to {HOST}")
        if HOST == '0.0.0.0':
            print("This exposes TrackerSpotter to ALL network interfaces.")
        else:
            print("This exposes TrackerSpotter to your network.")
        print("\nMake sure your firewall is configured appropriately!")
        print("="*60 + "\n")
    
    # Find available port (tries preferred port first, then increments)
    try:
        PORT = find_available_port(PREFERRED_PORT)
        if PORT != PREFERRED_PORT:
            try:
                print(f"\n⚠️  Port {PREFERRED_PORT} is busy, using port {PORT} instead")
            except UnicodeEncodeError:
                print(f"\n[!] Port {PREFERRED_PORT} is busy, using port {PORT} instead")
            print(f"   Check the dashboard for the correct tracker URL!\n")
    except OSError as e:
        try:
            print(f"\n❌ ERROR: Could not find an available port")
        except UnicodeEncodeError:
            print(f"\n[X] ERROR: Could not find an available port")
        print(f"   {e}")
        print(f"\n   Try closing other applications and restart TrackerSpotter.\n")
        sys.exit(1)
    
    # Print banner with actual port
    print_banner(HOST, PORT, ENABLE_IPV6)
    
    # Start server in main thread
    server = TrackerServer(host=HOST, port=PORT, debug=DEBUG, enable_ipv6=ENABLE_IPV6)
    
    # Start system tray icon
    tray_icon = None
    if is_tray_available():
        def on_exit():
            print("\n\nShutting down TrackerSpotter via tray... Goodbye!")
            sys.exit(0)
        
        tray_icon = TrayIcon(host=HOST, port=PORT, on_exit=on_exit)
        tray_icon.start()
    
    # Open browser in background thread (if enabled)
    if AUTO_BROWSER:
        # Use localhost for browser URL even if bound to 0.0.0.0
        browser_host = '127.0.0.1' if HOST == '0.0.0.0' else HOST
        url = f"http://{browser_host}:{PORT}"
        browser_thread = threading.Thread(target=open_browser, args=(url,), daemon=True)
        browser_thread.start()
    
    try:
        # Run server (blocks)
        server.run()
    except KeyboardInterrupt:
        if tray_icon:
            tray_icon.stop()
        print("\n\nShutting down TrackerSpotter... Goodbye!")
        sys.exit(0)
    except OSError as e:
        if "Address already in use" in str(e):
            # This should rarely happen now due to auto port detection
            print(f"\n❌ ERROR: Port {PORT} is already in use!")
            print(f"\n   This is unexpected - the port was available moments ago.")
            print(f"   Another application may have grabbed it. Please restart TrackerSpotter.\n")
            sys.exit(1)
        else:
            print(f"\n❌ ERROR: Failed to start server: {e}\n")
            sys.exit(1)
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

