# TrackerSpotter 🎯

**A local BitTorrent tracker monitor that captures and displays exactly what your torrent client reports to trackers.**

Perfect for QA, developers, and power users who need to validate torrent client behavior, debug announce issues, or understand the BitTorrent protocol.

<div align="center">

### 📥 Download TrackerSpotter v1.1.3

| Platform | Download | Notes |
|:--------:|:--------:|:------|
| 🪟 **Windows** | [![Download](https://img.shields.io/badge/Download-Windows-0078D4?style=for-the-badge&logo=windows&logoColor=white)](https://github.com/jbesclapez/TrackerSpotter/releases/download/v1.1.3/TrackerSpotter_v1.1.3_Windows.zip) | Single .exe • No install • 52 MB |
| 🍎 **macOS** | [![Download](https://img.shields.io/badge/Download-macOS-000000?style=for-the-badge&logo=apple&logoColor=white)](https://github.com/jbesclapez/TrackerSpotter/releases/download/v1.1.3/TrackerSpotter_v1.1.3_macOS.dmg) | .app bundle • ~50 MB |
| 🐧 **Linux** | [![Download](https://img.shields.io/badge/Download-Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)](https://github.com/jbesclapez/TrackerSpotter/releases/download/v1.1.3/TrackerSpotter_v1.1.3_Linux.tar.gz) | Binary + installer • ~45 MB |

**[📋 View All Releases](https://github.com/jbesclapez/TrackerSpotter/releases)** • **[📖 Installation Guide](#-quick-start)**

</div>

---

✅ **Cross-platform:** Windows, macOS, and Linux support

![Version](https://img.shields.io/badge/version-1.1.3-blue.svg)
![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

- 🎯 **Real-time Event Monitoring** - See announces appear instantly as they happen
- 🚀 **HTTP & UDP Tracker Support** - Both protocols supported (UDP is faster!)
- 📊 **Complete Progress Tracking** - Download, upload, and remaining bytes for every announce
- 🔍 **Smart Filtering** - Filter by event type, torrent, time range, or search anything
- 📁 **Export Capabilities** - Export session data to CSV or JSON with raw query strings
- 🐳 **Docker Compatible** - Works with Docker containers using host.docker.internal
- 🖥️ **Zero Installation** - Single executable, no admin rights needed
- 🌐 **Browser-based UI** - Clean, modern dashboard with real-time WebSocket updates
- 🔒 **Local Only** - Runs on localhost by default for security
- 🌍 **IPv6 Support** - Optional IPv6 binding with `--ipv6` flag
- 📡 **Scrape Support** - Logs HTTP and UDP tracker scrape requests
- 🔌 **Offline Mode** - Works without internet connection (bundled Socket.IO)
- 🖱️ **System Tray** - Minimize to tray with quick access menu
- 🔐 **Secure by Default** - Random session keys, input validation, localhost-only binding

## 🚀 Quick Start

### For End Users

#### Windows
1. **Download** the [latest release](https://github.com/jbesclapez/TrackerSpotter/releases/latest) (click the big blue button above!)
2. **Extract** the ZIP file
3. **Double-click** `TrackerSpotter.exe` to run (browser opens automatically, tray icon appears)
4. **Copy a tracker URL** from the dashboard

#### macOS
1. **Download** `TrackerSpotter_v1.1.3_macOS.dmg` or `.zip` from the [releases page](https://github.com/jbesclapez/TrackerSpotter/releases)
2. **Drag to Applications** (or run directly from .zip)
3. **Right-click → Open** (first time only, to bypass Gatekeeper)
4. **Copy a tracker URL** from the dashboard

#### Linux
1. **Download** `TrackerSpotter_v1.1.3_Linux.tar.gz` from the [releases page](https://github.com/jbesclapez/TrackerSpotter/releases)
2. **Extract and install**: `sudo ./install.sh` (or run `./trackerspotter` directly)
3. **Copy a tracker URL** from the dashboard

### Tracker URLs
- **UDP** (recommended): `udp://127.0.0.1:6969/announce`
- **HTTP**: `http://127.0.0.1:6969/announce`

### Configure Your Torrent Client
- **qBittorrent**: Right-click torrent → Edit trackers → Add URL
- **Transmission**: Edit torrent properties → Trackers → Add
- **Deluge**: Right-click torrent → Edit Trackers → Add

**Start your torrent** and watch events appear in real-time! 🎉

💡 **Tip:** UDP is faster and preferred by most torrent clients!

### For Developers

```bash
# Clone the repository
git clone https://github.com/jbesclapez/TrackerSpotter.git
cd TrackerSpotter

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt

# Run TrackerSpotter
python trackerspotter.py
```

Browser will open to `http://localhost:6969`

## 📸 Screenshots

### Main Dashboard
*Real-time event monitoring with filtering and search*

```
┌──────────────────────────────────────────────────────────────────────────┐
│ Time            Event      Torrent              Client        Progress   │
├──────────────────────────────────────────────────────────────────────────┤
│ 14:25:12.456   UPDATE    Ubuntu 22.04 ISO    qBittorrent    ↓ 142 MB    │
│ 14:24:32.789   UPDATE    Ubuntu 22.04 ISO    qBittorrent    ↓ 67 MB     │
│ 14:23:45.123   STARTED   Ubuntu 22.04 ISO    qBittorrent    ↓ 0 MB      │
└──────────────────────────────────────────────────────────────────────────┘
```

### Event Detail Panel
*Click any event to see complete details including all reported parameters*

## 🎮 Usage Examples

### Validate Client Behavior

**Scenario**: Verify your torrent client sends proper "completed" events

1. Add a test torrent with TrackerSpotter's URL
2. Let it download completely
3. Look for `COMPLETED` event with `left: 0 bytes` ✓

### Debug Upload Reporting

**Scenario**: Client shows upload but tracker doesn't receive it

1. Monitor announces during seeding
2. Check "uploaded" values in each update
3. Compare with client's reported upload
4. Export to CSV for detailed analysis

### Test Multiple Torrents

**Scenario**: Ensure client handles multiple torrents correctly

1. Add multiple test torrents with TrackerSpotter URL
2. Start all torrents simultaneously
3. Use the torrent filter dropdown to view each independently
4. Verify all send proper started/completed/stopped events

## 🔧 Configuration

TrackerSpotter can be configured via command-line arguments:

```bash
# Default: localhost only on port 6969
trackerspotter

# Change port
trackerspotter --port 8080

# Expose to LAN (requires firewall configuration)
trackerspotter --host 0.0.0.0

# Bind to specific interface
trackerspotter --host 192.168.1.5

# Enable IPv6 support
trackerspotter --ipv6

# Don't auto-open browser
trackerspotter --no-browser

# See all options
trackerspotter --help
```

**Note:** When binding to non-localhost addresses, make sure to configure your firewall appropriately.

## 🧪 Creating Test Torrents

You can create your own test torrents using any torrent client or command-line tools:

```bash
# Using mktorrent (Linux/macOS)
mktorrent -a http://127.0.0.1:6969/announce -o test.torrent test_file.txt

# Using transmission-create (cross-platform)
transmission-create -t http://127.0.0.1:6969/announce -o test.torrent test_file.txt

# Using py3createtorrent (Python)
pip install py3createtorrent
py3createtorrent -t http://127.0.0.1:6969/announce test_file.txt
```

Sample test files are included in the `test_torrents/` directory of the source repository.

## 📋 What Gets Captured

For every announce, TrackerSpotter records:

| Field | Description |
|-------|-------------|
| **Timestamp** | Precise local time with milliseconds |
| **Event Type** | started, completed, stopped, or update |
| **Torrent Info** | Info hash and friendly name |
| **Client Info** | IP address, port, peer ID, user agent |
| **Progress** | Uploaded, downloaded, and remaining bytes |
| **All Parameters** | Complete query string for debugging |
| **Raw HTTP Headers** | Complete HTTP headers as sent by client |

## 🎯 Common Use Cases

- ✅ Validate QA test scenarios for torrent client development
- ✅ Debug why a client isn't reporting properly to trackers
- ✅ Understand BitTorrent protocol by seeing real announces
- ✅ Compare behavior between different torrent clients
- ✅ Verify upload/download counter accuracy
- ✅ Educational tool for learning tracker communication

## 📚 Supported Torrent Clients

Tested and confirmed working with:

- ✅ qBittorrent (4.3+)
- ✅ Transmission (3.0+)
- ✅ Deluge (2.0+)
- ✅ μTorrent/BitTorrent (latest)
- ✅ BiglyBT
- ✅ Tixati

*Any client that supports HTTP tracker announces will work!*

## 💻 Compatibility Notes

### Windows 7 (Unsupported but Possible)

While Python 3.9+ doesn't officially support Windows 7, TrackerSpotter can run under Windows 7 using [VxKex](https://github.com/vxiiduu/VxKex) with these settings:

- **Enable VxKex for this program:** Yes
- **Report a different version of Windows:** Windows 10
- **Use stronger version reporting:** Yes
- **Disable VxKex for child processes:** Yes (important!)

*Note: This configuration is community-tested but not officially supported.*

## 🛠️ Building from Source

### Prerequisites

```bash
# Install development dependencies
pip install -r requirements.txt
pip install pyinstaller
```

### Build for Your Platform

#### Windows
```bash
python build_scripts/build_windows.py
# Output: dist/TrackerSpotter.exe
```

#### macOS
```bash
python build_scripts/build_macos.py
# Output: dist/TrackerSpotter.app and dist/TrackerSpotter_v1.1.3_macOS.dmg
```

#### Linux
```bash
python build_scripts/build_linux.py
# Output: dist/trackerspotter and dist/TrackerSpotter_v1.1.3_Linux.tar.gz
```

### Generate Icons (All Platforms)

```bash
python build_scripts/generate_icons.py
# Creates PNG, ICO, and ICNS icons in icons/ directory
```

## 🐛 Troubleshooting

### Port Already in Use

**Error**: "Port 6969 is already in use"

**Solution**: 
- Close other applications using port 6969
- Or change port in Settings

### No Events Appearing

**Checklist**:
1. ✓ Is TrackerSpotter running? (check system tray icon)
2. ✓ Did you copy the correct URL? (`http://127.0.0.1:6969/announce`)
3. ✓ Is the torrent started/active in your client?
4. ✓ Does your client allow custom trackers?

### Browser Doesn't Open

- Use `--no-browser` flag and manually navigate to `http://127.0.0.1:6969`
- Check the system tray icon - right-click and select "Open Dashboard"
- Check Windows Firewall isn't blocking local connections

### Firewall Prompt on Startup

If you see a Windows Firewall prompt, it's likely because:
- UDP tracker is binding (this is needed for UDP announce support)
- You're using `--host 0.0.0.0` to expose to LAN

For localhost-only use, you can safely deny the firewall request.

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Ideas for enhancements**:
- Additional torrent client setup guides
- UI themes (dark mode, high contrast)
- Internationalization (i18n)
- Performance optimizations
- Additional export formats

## 📜 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- BitTorrent Protocol: [BEP 3](http://www.bittorrent.org/beps/bep_0003.html)
- Tracker specification: [BEP 3 - Tracker Protocol](https://www.bittorrent.org/beps/bep_0003.html)

## 📞 Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/jbesclapez/TrackerSpotter/issues)
- 💬 **Questions**: [GitHub Discussions](https://github.com/jbesclapez/TrackerSpotter/discussions)
- 📧 **Email**: Create an issue on GitHub

## 📦 What's Included

TrackerSpotter v1.1.3 is a complete, production-ready monitoring solution with:

- ✅ HTTP and UDP tracker implementations (BEP 3, BEP 15)
- ✅ Scrape request support
- ✅ IPv6 dual-stack support
- ✅ Real-time WebSocket updates
- ✅ Comprehensive event logging with raw headers
- ✅ CSV/JSON export capabilities
- ✅ System tray integration
- ✅ Cross-platform builds (Windows, macOS, Linux)
- ✅ Offline operation (no internet required)
- ✅ Security hardening (input validation, random keys, localhost-only default)

This is a stable, feature-complete release suitable for production use.

---

**Made with ❤️ for the BitTorrent community**

*Star ⭐ this repository if you find it useful!*


