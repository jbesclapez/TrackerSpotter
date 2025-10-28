"""
TrackerSpotter - Main entry point
"""

import sys
import webbrowser
import threading
import time
import socket
from pathlib import Path

from . import __version__
from .tracker_server import TrackerServer


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
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            test_socket.bind(('127.0.0.1', port))
            test_socket.close()
            return port
        except OSError:
            continue
    
    raise OSError(f"No available ports found in range {start_port}-{start_port + max_attempts - 1}")


def print_banner(host: str, port: int):
    """
    Print startup banner
    
    Args:
        host: Server host
        port: Server port
    """
    # Try to set UTF-8 encoding for better character support
    import sys
    import io
    
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
    
    banner = f"""
================================================================
                  TrackerSpotter v{__version__}
           Local BitTorrent Tracker Monitor
================================================================

  Status: Running
  
  HTTP Tracker: http://{host}:{port}/announce
  UDP Tracker:  udp://{host}:{port}/announce
  Dashboard:    http://{host}:{port}

  Copy a tracker URL above and add it to your torrent
  client to start monitoring announces!
  
  Tip: UDP is faster and preferred by most clients

  Press Ctrl+C to stop
================================================================
"""
    print(banner)


def main():
    """Main entry point for TrackerSpotter"""
    
    # Configuration (could be loaded from config file in future)
    HOST = "127.0.0.1"  # Localhost only by default for security
    DEBUG = False
    
    # Find available port (tries 6969 first, then 6970, 6971, etc.)
    try:
        PORT = find_available_port(6969)
        if PORT != 6969:
            print(f"\n⚠️  Port 6969 is busy, using port {PORT} instead")
            print(f"   Check the dashboard for the correct tracker URL!\n")
    except OSError as e:
        print(f"\n❌ ERROR: Could not find an available port")
        print(f"   {e}")
        print(f"\n   Try closing other applications and restart TrackerSpotter.\n")
        sys.exit(1)
    
    # Print banner with actual port
    print_banner(HOST, PORT)
    
    # Start server in main thread
    server = TrackerServer(host=HOST, port=PORT, debug=DEBUG)
    
    # Open browser in background thread
    url = f"http://{HOST}:{PORT}"
    browser_thread = threading.Thread(target=open_browser, args=(url,), daemon=True)
    browser_thread.start()
    
    try:
        # Run server (blocks)
        server.run()
    except KeyboardInterrupt:
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

