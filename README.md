# TrackerSpotter 🎯

**A local BitTorrent tracker monitor for Windows that captures and displays exactly what your torrent client reports to trackers.**

Perfect for QA, developers, and power users who need to validate torrent client behavior, debug announce issues, or understand the BitTorrent protocol.

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

- 🎯 **Real-time Event Monitoring** - See announces appear instantly as they happen
- 🚀 **HTTP & UDP Tracker Support** - Both protocols supported (UDP is faster!)
- 📊 **Complete Progress Tracking** - Download, upload, and remaining bytes for every announce
- 🔍 **Smart Filtering** - Filter by event type, torrent, time range, or search anything
- 📁 **Export Capabilities** - Export session data to CSV or JSON
- 🧪 **Test Kit Included** - Create dummy torrents for easy testing
- 🐳 **Docker Compatible** - Works with Docker containers using host.docker.internal
- 🖥️ **Zero Installation** - Single executable, no admin rights needed
- 🌐 **Browser-based UI** - Clean, modern dashboard with real-time updates
- 🔒 **Local Only** - Runs on localhost by default for security
- 🌐 **IPv6 Support** - Optional IPv6 binding with `--ipv6` flag
- 📡 **Scrape Support** - Logs tracker scrape requests
- 🔌 **Offline Mode** - Works without internet connection

## 🚀 Quick Start

### For End Users (Windows)

1. **Download** `TrackerSpotter.exe` from the [releases page](https://github.com/jbesclapez/TrackerSpotter/releases)
2. **Double-click** to run (your browser will open automatically)
3. **Copy a tracker URL** from the dashboard:
   - **UDP** (recommended): `udp://127.0.0.1:6969/announce`
   - **HTTP**: `http://127.0.0.1:6969/announce`
4. **Configure your torrent client**:
   - In qBittorrent: Right-click torrent → Edit trackers → Add the URL above
   - In Transmission: Edit torrent properties → Trackers → Add
   - In Deluge: Right-click torrent → Edit Trackers → Add
5. **Start your torrent** and watch events appear in real-time! 🎉

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

1. Use the Test Kit to generate 5 dummy torrents
2. Add all to your client with TrackerSpotter URL
3. Use filters to view each torrent independently
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

## 🧪 Test Kit (CLI)

Generate dummy torrents for testing via command line:

```bash
# Run the test kit generator
python -m trackerspotter.test_kit

# Or specify tracker URL directly
python -m trackerspotter.test_kit http://127.0.0.1:6969/announce
```

This creates 5 test torrents of varying sizes (1KB to 10MB) in a `test_torrents/` directory.

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

### Build Windows Executable

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run build script
python build_scripts/build_windows.py

# Output: dist/TrackerSpotter.exe
```

### Run Tests

```bash
pytest tests/ -v --cov=src
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

**Areas we'd love help with**:
- Additional torrent client guides
- UI/UX improvements
- Cross-platform support (macOS, Linux)
- Internationalization
- Performance optimizations

## 📜 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- BitTorrent Protocol: [BEP 3](http://www.bittorrent.org/beps/bep_0003.html)
- Tracker specification: [BEP 3 - Tracker Protocol](https://www.bittorrent.org/beps/bep_0003.html)

## 📞 Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/jbesclapez/TrackerSpotter/issues)
- 💬 **Questions**: [GitHub Discussions](https://github.com/jbesclapez/TrackerSpotter/discussions)
- 📧 **Email**: Create an issue on GitHub

## 🗺️ Roadmap

- [x] v1.0: HTTP & UDP tracker support ✅
- [x] v1.1: Scrape support, IPv6, configurable binding ✅
- [ ] v1.2: Export to chart/graph visualizations
- [ ] v1.3: Compare sessions feature
- [ ] v1.4: Torrent name/labeling feature
- [ ] v2.0: Cross-platform support (macOS, Linux)
- [ ] v2.1: DHT monitoring (separate from tracker)
- [ ] v2.2: Packet sniffing and deep inspection

---

**Made with ❤️ for the BitTorrent community**

*Star ⭐ this repository if you find it useful!*

