# Changelog

All notable changes to TrackerSpotter will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-10-26

### Added
- Initial release of TrackerSpotter
- HTTP BitTorrent tracker implementation (BEP 3)
- Real-time event monitoring with WebSocket updates
- Web-based dashboard with modern UI
- SQLite database for event storage
- Event filtering by type, torrent, and search
- CSV and JSON export functionality
- Test kit for generating dummy torrents
- Windows executable packaging with PyInstaller
- Comprehensive documentation (README, Usage Guide, Contributing)
- Event detail panel with complete announce information
- Statistics dashboard (total events, unique torrents, event counts)
- Client information extraction from User-Agent and peer ID
- Auto-opening browser on startup
- Clean, accessible UI with keyboard navigation
- Local-only security by default (localhost binding)

### Features
- **Tracker Server**
  - HTTP announce endpoint
  - Bencode response generation
  - Minimal valid tracker responses
  - Error handling for malformed requests

- **Event Tracking**
  - Started, completed, stopped, and update events
  - Upload, download, and remaining byte tracking
  - Client IP, port, and user agent capture
  - Timestamp with millisecond precision
  - Raw query string storage for debugging

- **Web Dashboard**
  - Real-time event table with filtering
  - Statistics cards
  - Search functionality
  - Detail panel for event inspection
  - Responsive design for mobile/desktop
  - WebSocket-based live updates

- **Data Export**
  - CSV export for spreadsheet analysis
  - JSON export for programmatic use
  - Includes all captured fields

- **Test Kit**
  - Generate 5 test torrents (1KB to 10MB)
  - Create matching dummy files
  - Custom tracker URL support

- **Packaging**
  - Single-file Windows executable
  - Distribution package with documentation
  - Console version for debugging

### Technical
- Python 3.9+ support
- Flask web framework
- Flask-SocketIO for real-time updates
- SQLite for persistent storage
- Modern JavaScript (ES6+)
- CSS custom properties for theming
- Indexed database queries for performance

### Documentation
- Comprehensive README with quick start
- Detailed usage guide
- Contributing guidelines
- Cursor rules for development
- Build instructions
- Troubleshooting section

## [1.1.3] - 2025-01-XX

### Fixed
- Release asset uploads now work correctly on tag push
- GitHub Actions workflow now uploads files automatically when tags are pushed
- Download links in README now work correctly

## [1.1.2] - 2025-01-XX

### Fixed
- Linux build failures in CI environments (pystray/Xlib display issues)
- Dependency verification now skipped in CI to prevent X display initialization
- Improved CI detection with multiple environment variable checks

### Changed
- Cleaned up verbose debug output from CI fixes
- Updated README download links to v1.1.2

### Technical
- Build scripts now detect CI environments and skip dependency verification
- Xvfb properly configured for headless Linux builds
- More robust CI environment detection

## [1.1.0] - 2025-11-30

### Added - Protocol Support
- UDP tracker implementation (BEP 15) - Faster and more efficient than HTTP
- HTTP and UDP scrape support - Monitor tracker statistics requests
- IPv6 dual-stack support with `--ipv6` flag
- Simultaneous HTTP and UDP trackers on same port
- Protocol detection badges (HTTP/UDP) in event list
- Real-time WebSocket broadcasting of UDP events

### Added - Security & Stability
- Random session key generation (no hardcoded secrets)
- Input validation with bounds checking for all announce parameters
- Periodic UDP connection cleanup (prevents memory leak)
- Event memory capping (max 1000 in browser to prevent crashes)
- Safe integer parsing with min/max validation

### Added - Cross-Platform Support
- macOS build script (`build_macos.py`) for .app bundle creation
- Linux build script (`build_linux.py`) with install/uninstall scripts
- Cross-platform database paths (Windows/macOS/Linux)
- Cross-platform clipboard support in system tray
- Icon generation script for PNG/ICO/ICNS formats
- Complete icon sets for all platforms

### Added - Features
- System tray icon with context menu
- Raw HTTP headers capture and display
- Configurable bind interface via `--host` flag
- Configurable port via `--port` flag
- `--no-browser` flag to prevent auto-opening browser
- Docker-compatible tracker URLs in UI
- IPv6 tracker URLs when enabled
- Version display in footer (dynamically loaded)

### Fixed
- SQL reserved keyword issue with 'unique' in stats query
- BLOB to JSON serialization for info_hash field
- Events persist correctly across page refreshes
- 500 error when loading events from database
- Protocol detection bug (HTTP was showing as UDP)
- Clear logs now resets torrent filter counts
- Tip text visibility (was dark gray on purple)

### Changed
- CSV exports now include raw_query column
- Version management: single source of truth in `__init__.py`
- UDP tracker binds to 127.0.0.1 by default (no firewall prompt)
- Enhanced Quick Start banner with 4 tracker URL options
- Improved startup banner with HTTP, UDP, and IPv6 URLs
- Enhanced error logging with full tracebacks
- Socket.IO bundled locally for offline operation

### Technical
- Bumped version to 1.1.0
- Added `secrets` module for cryptographic key generation
- Socket timeout on UDP for periodic cleanup checks
- Build scripts now read version from `__init__.py`
- Cross-platform `get_app_data_dir()` function

---

[1.1.3]: https://github.com/jbesclapez/TrackerSpotter/releases/tag/v1.1.3
[1.1.2]: https://github.com/jbesclapez/TrackerSpotter/releases/tag/v1.1.2
[1.1.0]: https://github.com/jbesclapez/TrackerSpotter/releases/tag/v1.1.0
[1.0.0]: https://github.com/jbesclapez/TrackerSpotter/releases/tag/v1.0.0

