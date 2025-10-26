# TrackerSpotter 🎯

**A local BitTorrent tracker monitor for Windows that captures and displays exactly what your torrent client reports to trackers.**

Perfect for QA, developers, and power users who need to validate torrent client behavior, debug announce issues, or understand the BitTorrent protocol.

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

- 🎯 **Real-time Event Monitoring** - See announces appear instantly as they happen
- 📊 **Complete Progress Tracking** - Download, upload, and remaining bytes for every announce
- 🔍 **Smart Filtering** - Filter by event type, torrent, time range, or search anything
- 📁 **Export Capabilities** - Export session data to CSV or JSON
- 🧪 **Test Kit Included** - Create dummy torrents for easy testing
- 🖥️ **Zero Installation** - Single executable, no admin rights needed
- 🌐 **Browser-based UI** - Clean, modern dashboard with real-time updates
- 🔒 **Local Only** - Runs on localhost by default for security

## 🚀 Quick Start

### For End Users (Windows)

1. **Download** `TrackerSpotter.exe` from the [releases page](https://github.com/jbesclapez/TrackerSpotter/releases)
2. **Double-click** to run (your browser will open automatically)
3. **Copy the tracker URL** shown in the dashboard: `http://127.0.0.1:6969/announce`
4. **Configure your torrent client**:
   - In qBittorrent: Right-click torrent → Edit trackers → Add the URL above
   - In Transmission: Edit torrent properties → Trackers → Add
   - In Deluge: Right-click torrent → Edit Trackers → Add
5. **Start your torrent** and watch events appear in real-time! 🎉

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

Access settings via the **⚙️ Settings** button in the UI:

- **Port**: Change listening port (default: 6969)
- **Log Retention**: Set max days or file size for logs
- **Verbose Mode**: Show additional technical details
- **Auto-open Browser**: Enable/disable browser launch on startup

## 🧪 Test Kit

Create dummy torrents for testing:

1. Click **🧪 Test Kit** in the dashboard
2. Follow the guided steps to generate 5 test torrents
3. Includes tiny files (1KB each) for quick testing
4. Pre-configured to use your TrackerSpotter URL

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
1. ✓ Is TrackerSpotter running? (check system tray)
2. ✓ Did you copy the correct URL? (`http://127.0.0.1:6969/announce`)
3. ✓ Is the torrent started/active in your client?
4. ✓ Does your client allow custom trackers?

### Browser Doesn't Open

- Manually navigate to `http://localhost:6969`
- Check Windows Firewall isn't blocking local connections

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Areas we'd love help with**:
- UDP tracker support
- Additional torrent client guides
- UI/UX improvements
- Cross-platform support (macOS, Linux)
- Internationalization

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

- [ ] v1.1: UDP tracker support
- [ ] v1.2: Export to chart/graph visualizations
- [ ] v1.3: Compare sessions feature
- [ ] v2.0: Cross-platform support (macOS, Linux)
- [ ] v2.1: DHT monitoring (separate from tracker)

---

**Made with ❤️ for the BitTorrent community**

*Star ⭐ this repository if you find it useful!*

