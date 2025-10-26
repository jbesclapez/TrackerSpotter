"""
TrackerSpotter - Main entry point
"""

import sys
import webbrowser
import threading
import time
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
  Tracker URL: http://{host}:{port}/announce
  Dashboard:   http://{host}:{port}

  Copy the tracker URL above and add it to your torrent
  client to start monitoring announces!

  Press Ctrl+C to stop
================================================================
"""
    print(banner)


def main():
    """Main entry point for TrackerSpotter"""
    
    # Configuration (could be loaded from config file in future)
    HOST = "127.0.0.1"  # Localhost only by default for security
    PORT = 6969  # Common BitTorrent tracker port
    DEBUG = False
    
    # Print banner
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
            print(f"\nERROR: Port {PORT} is already in use!")
            print(f"\nSolutions:")
            print(f"  1. Stop the other application using port {PORT}")
            print(f"  2. Or modify the PORT variable in the script")
            sys.exit(1)
        else:
            print(f"\nERROR: Failed to start server: {e}")
            sys.exit(1)
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

