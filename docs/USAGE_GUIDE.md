# TrackerSpotter Usage Guide

## Table of Contents

1. [Getting Started](#getting-started)
2. [Setting Up Your Torrent Client](#setting-up-your-torrent-client)
3. [Understanding the Dashboard](#understanding-the-dashboard)
4. [Using Filters and Search](#using-filters-and-search)
5. [Exporting Data](#exporting-data)
6. [Test Kit Usage](#test-kit-usage)
7. [Troubleshooting](#troubleshooting)

## Getting Started

### Running TrackerSpotter

**Option 1: Using the Executable (Windows)**
```
1. Download TrackerSpotter.exe
2. Double-click to run
3. Your browser will automatically open to the dashboard
```

**Option 2: Using Python**
```bash
# Make sure Python 3.9+ is installed
python trackerspotter.py
```

Once running, you'll see:
```
╔════════════════════════════════════════════════════════════════╗
║                      TrackerSpotter v1.0.0                     ║
║           Local BitTorrent Tracker Monitor                     ║
╠════════════════════════════════════════════════════════════════╣
║  Status: ✓ Running                                            ║
║  Tracker URL: http://127.0.0.1:6969/announce                  ║
║  Dashboard:   http://127.0.0.1:6969                           ║
╚════════════════════════════════════════════════════════════════╝
```

**Important**: Keep this window open while using TrackerSpotter. Closing it will stop the tracker.

## Setting Up Your Torrent Client

To monitor torrent activity, you need to configure your client to use TrackerSpotter as a tracker.

### qBittorrent

1. **Right-click** a torrent in your list
2. Select **"Edit tracker..."** or **"Edit torrent..."**
3. Click **"Add"** or paste in the tracker list
4. Enter: `http://127.0.0.1:6969/announce`
5. Click **OK**

**Tip**: You can keep your existing tracker or replace it entirely. For testing, replacing gives cleaner results.

### Transmission

1. **Right-click** a torrent
2. Select **"Properties"**
3. Go to the **"Tracker"** tab
4. Click **"+"** to add a new tracker
5. Enter: `http://127.0.0.1:6969/announce`
6. Click **OK**

### Deluge

1. **Right-click** a torrent
2. Select **"Edit Trackers"**
3. Click **"Add"**
4. Enter: `http://127.0.0.1:6969/announce`
5. Click **OK**

### μTorrent / BitTorrent Client

1. **Right-click** a torrent
2. Select **"Properties"**
3. In the **Trackers** section, add a new line
4. Enter: `http://127.0.0.1:6969/announce`
5. Click **OK**

## Understanding the Dashboard

### Top Stats Cards

- **Total Events**: Total number of announces received
- **Unique Torrents**: Number of different torrents tracked
- **Started**: Number of "started" events
- **Completed**: Number of "completed" events

### Events Table

The main table shows all announce events with these columns:

| Column | Description |
|--------|-------------|
| **Time** | Precise timestamp (HH:MM:SS.mmm) |
| **Event** | Type: STARTED, COMPLETED, STOPPED, or UPDATE |
| **Torrent** | Short info hash (first 8 characters) |
| **Client** | IP address and port of the client |
| **Downloaded** | Total bytes downloaded |
| **Uploaded** | Total bytes uploaded |
| **Remaining** | Bytes left to download |
| **Progress** | Visual progress bar and percentage |

### Event Types Explained

- **STARTED** (Green): Client begins downloading/seeding
- **COMPLETED** (Blue): Download finished
- **STOPPED** (Red): Torrent stopped or removed
- **UPDATE** (Gray): Regular progress update (typically every 30-60 seconds)

### Event Details Panel

Click any row to open detailed information:

- Full info hash
- Complete client information (peer ID, user agent)
- Exact byte counts
- All additional parameters sent by the client
- Raw query string (for debugging)

**Close the panel**: Click the X, press Escape, or click outside the panel

## Using Filters and Search

### Filter by Event Type

Use the **"All Events"** dropdown to show only:
- Started events
- Completed events
- Stopped events
- Updates (periodic announces)

### Filter by Torrent

The **"All Torrents"** dropdown lists all unique torrents with event counts:
```
3a7f9b2c... (27)
├─ Info hash preview
└─ Number of events
```

Select one to see only its events.

### Search Box

Search across multiple fields:
- Info hash
- Client IP address
- User agent string

**Example searches**:
- `3a7f9b2c` - Find specific torrent
- `127.0.0.1` - Find local announces
- `qBittorrent` - Find events from qBittorrent client

### Combining Filters

All filters work together:
1. Select "Completed" event type
2. Choose a specific torrent
3. Search for "qBittorrent"

Result: Only completed events for that torrent from qBittorrent

## Exporting Data

### Export to CSV

Click **"📊 Export CSV"** to download a spreadsheet-compatible file:

```csv
timestamp,event,info_hash,client_ip,downloaded,uploaded,left,user_agent
2025-10-26 14:23:45.123,started,3a7f9b2c...,127.0.0.1:52341,0,0,3435973836,"qBittorrent/4.6.0"
```

**Use cases**:
- Open in Excel or Google Sheets
- Analyze trends over time
- Share with team members
- Compare client behaviors

### Export to JSON

Click **"📄 Export JSON"** for structured data:

```json
{
  "export_date": "2025-10-26T14:30:00",
  "total_events": 150,
  "events": [
    {
      "id": 1,
      "timestamp": "2025-10-26T14:23:45.123",
      "event": "started",
      "info_hash_hex": "3a7f9b2c...",
      ...
    }
  ]
}
```

**Use cases**:
- Programmatic analysis
- Import into other tools
- Archive session data
- Automated testing validation

## Test Kit Usage

TrackerSpotter includes a test kit to generate dummy torrents for quick testing.

### Generate Test Torrents

**Option 1: Built-in Generator**
```bash
python -m src.trackerspotter.test_kit
```

**Option 2: Custom Tracker URL**
```bash
python -m src.trackerspotter.test_kit http://192.168.1.100:6969/announce
```

This creates 5 test torrents:
- **test_tiny** (1 KB)
- **test_small** (10 KB)
- **test_medium** (100 KB)
- **test_large** (1 MB)
- **test_xlarge** (10 MB)

### Using Test Torrents

1. Run the test kit (creates .torrent files in `test_torrents/`)
2. Optionally create matching dummy files when prompted
3. Add the .torrent files to your torrent client
4. Start the torrents
5. Watch events appear in real-time!

**Perfect for**:
- Learning how BitTorrent announces work
- Testing TrackerSpotter features
- Validating client configurations
- Training and demonstrations

## Troubleshooting

### Port Already in Use

**Problem**: "Port 6969 is already in use"

**Solutions**:
1. Close other applications using port 6969
2. Check if another instance of TrackerSpotter is running
3. Modify the `PORT` variable in `trackerspotter.py`

### No Events Appearing

**Checklist**:

✓ **Is TrackerSpotter running?**
  - Check for the console window
  - Dashboard should show "Connected" status

✓ **Is the tracker URL correct?**
  - Must be exactly: `http://127.0.0.1:6969/announce`
  - Copy button ensures no typos

✓ **Is the torrent active?**
  - Make sure it's not paused
  - Check if your client is "announcing"

✓ **Does your client allow custom trackers?**
  - Some clients restrict tracker editing
  - Try with a known-compatible client (qBittorrent, Transmission)

✓ **Are you using the right IP?**
  - For local testing: `127.0.0.1`
  - For network testing: Your machine's IP address

### Browser Doesn't Open Automatically

**Solution**: Manually navigate to `http://127.0.0.1:6969` in your browser

### Events Not Updating in Real-time

**Problem**: Have to refresh manually to see new events

**Solutions**:
1. Check WebSocket connection status (top right of dashboard)
2. Disable browser extensions that block WebSockets
3. Check firewall isn't blocking local connections
4. Try a different browser (Chrome, Firefox, Edge)

### Can't See Full Info Hash

**Solution**: Click the event row to open the detail panel with complete information

### Large Number of Events Slowing Down UI

**Solutions**:
1. Use filters to reduce displayed events
2. Click "🗑️ Clear All" to start fresh
3. Export old data first if needed
4. Restart TrackerSpotter for a clean session

### Firewall Warnings

**Problem**: Windows Firewall asks for permission

**Solution**: 
- Click "Allow" for private networks
- TrackerSpotter only listens on localhost by default
- Safe to allow for local-only use

## Advanced Tips

### Running on a Different Port

Edit `trackerspotter.py` or `src/trackerspotter/main.py`:

```python
PORT = 8080  # Change from 6969 to your preferred port
```

Remember to update your tracker URL: `http://127.0.0.1:8080/announce`

### Allowing Network Access

**⚠️ Security Warning**: Only do this on trusted networks

Edit `trackerspotter.py`:

```python
HOST = "0.0.0.0"  # Change from "127.0.0.1"
```

Now accessible from other machines: `http://YOUR_IP:6969/announce`

### Keyboard Shortcuts

- **Escape**: Close detail panel
- **Ctrl+R** or **F5**: Refresh events
- **Tab**: Navigate between controls

### Comparing Multiple Clients

1. Set up 2+ different torrent clients with TrackerSpotter
2. Add the same torrent to each
3. Use the "Client" column to identify which is which
4. Click events to see detailed client identification
5. Export data to compare behaviors

## Best Practices

### For QA Testing

1. Start with a clean session (Clear All)
2. Document your test scenario
3. Perform the test steps
4. Export results immediately
5. Compare with expected behavior

### For Development

1. Use test torrents for reproducible scenarios
2. Check both "started" and "completed" events
3. Validate counter values (uploaded, downloaded, left)
4. Review raw query strings for protocol compliance
5. Test edge cases (pause, resume, multiple torrents)

### For Learning

1. Start with one small test torrent
2. Watch the sequence: started → updates → completed → stopped
3. Observe update frequency (usually 30-60 seconds)
4. Try different clients to see variations
5. Review the detail panel for each event type

## Getting Help

- **Issues**: [GitHub Issues](https://github.com/jbesclapez/TrackerSpotter/issues)
- **Discussions**: [GitHub Discussions](https://github.com/jbesclapez/TrackerSpotter/discussions)
- **Documentation**: Check the README.md for quick reference

---

**Remember**: TrackerSpotter is a monitoring tool. It doesn't affect your actual torrent downloads, just observes what your client reports to trackers.

Happy tracking! 🎯

