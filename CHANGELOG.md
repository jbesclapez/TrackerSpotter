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

## [Unreleased]

### Added
- UDP tracker support (BEP 15) - Faster and more efficient than HTTP
- Both HTTP and UDP trackers run simultaneously on same port
- Real-time broadcasting of UDP events to dashboard via WebSocket
- Comprehensive UDP protocol implementation (connect, announce, scrape)
- Updated UI to show both HTTP and UDP tracker URLs
- Docker-specific tracker URLs in Quick Start guide

### Fixed
- SQL reserved keyword issue with 'unique' in stats query
- BLOB to JSON serialization for info_hash field
- Events now persist correctly across page refreshes
- 500 error when loading events from database

### Changed
- Quick Start banner now shows 4 tracker URL options (HTTP/UDP × Local/Docker)
- Improved startup banner with both HTTP and UDP tracker URLs
- Enhanced error logging with full tracebacks

### Planned Features
- Dark mode theme
- Chart/graph visualizations
- Session comparison
- Torrent name/labeling
- Cross-platform support (macOS, Linux)
- DHT monitoring
- Packet sniffing
- Internationalization

---

[1.0.0]: https://github.com/jbesclapez/TrackerSpotter/releases/tag/v1.0.0

