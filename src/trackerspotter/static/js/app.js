// TrackerSpotter - Main Application JavaScript

// Global state
let socket = null;
let allEvents = [];
let filteredEvents = [];
let currentFilters = {
    eventType: 'all',
    torrent: 'all',
    search: ''
};

// Configuration
const MAX_EVENTS_IN_MEMORY = 1000;  // Cap events to prevent memory issues

// Initialize application
document.addEventListener('DOMContentLoaded', () => {
    console.log('TrackerSpotter initializing...');
    updateTrackerUrls(); // Update URLs based on actual port
    initializeWebSocket();
    loadInitialData();
    setupEventListeners();
});

// Update tracker URLs dynamically based on server config
async function updateTrackerUrls() {
    try {
        const response = await fetch('/api/config');
        const data = await response.json();
        
        if (data.success) {
            const host = data.display_host;
            const port = data.port;
            
            // Update HTTP tracker URL
            const httpUrl = `http://${host}:${port}/announce`;
            const httpElement = document.getElementById('trackerUrlHttp');
            if (httpElement) {
                httpElement.textContent = httpUrl;
            }
            
            // Update HTTP Docker URL
            const httpDockerUrl = `http://host.docker.internal:${port}/announce`;
            const httpDockerElement = document.getElementById('trackerUrlHttpDocker');
            if (httpDockerElement) {
                httpDockerElement.textContent = httpDockerUrl;
            }
            
            // Update UDP tracker URL
            const udpUrl = `udp://${host}:${port}/announce`;
            const udpElement = document.getElementById('trackerUrlUdp');
            if (udpElement) {
                udpElement.textContent = udpUrl;
            }
            
            // Update UDP Docker URL
            const udpDockerUrl = `udp://host.docker.internal:${port}/announce`;
            const udpDockerElement = document.getElementById('trackerUrlUdpDocker');
            if (udpDockerElement) {
                udpDockerElement.textContent = udpDockerUrl;
            }
            
            // Handle IPv6 URLs if enabled
            const ipv6Section = document.getElementById('ipv6UrlsSection');
            if (data.ipv6_enabled && data.http_url_ipv6) {
                // Show IPv6 section
                if (ipv6Section) {
                    ipv6Section.style.display = 'block';
                }
                
                // Update IPv6 URLs
                const httpIpv6Element = document.getElementById('trackerUrlHttpIpv6');
                if (httpIpv6Element) {
                    httpIpv6Element.textContent = data.http_url_ipv6;
                }
                
                const udpIpv6Element = document.getElementById('trackerUrlUdpIpv6');
                if (udpIpv6Element) {
                    udpIpv6Element.textContent = data.udp_url_ipv6;
                }
            } else if (ipv6Section) {
                ipv6Section.style.display = 'none';
            }
            
            // Show warning if bound to non-localhost
            if (!data.is_localhost) {
                console.log(`TrackerSpotter is exposed on ${data.host}:${port}`);
            }
            
            // Update version display if available
            if (data.version) {
                const versionElement = document.getElementById('versionDisplay');
                if (versionElement) {
                    versionElement.textContent = `v${data.version}`;
                }
            }
            
            console.log(`Tracker URLs updated for ${host}:${port}`);
        }
    } catch (error) {
        // Fallback to window.location if API fails
        const port = window.location.port || '6969';
        const host = window.location.hostname || '127.0.0.1';
        
        document.getElementById('trackerUrlHttp').textContent = `http://${host}:${port}/announce`;
        document.getElementById('trackerUrlHttpDocker').textContent = `http://host.docker.internal:${port}/announce`;
        document.getElementById('trackerUrlUdp').textContent = `udp://${host}:${port}/announce`;
        document.getElementById('trackerUrlUdpDocker').textContent = `udp://host.docker.internal:${port}/announce`;
        
        console.log('Tracker URLs updated from window.location (fallback)');
    }
}

// WebSocket connection
function initializeWebSocket() {
    socket = io();
    
    socket.on('connect', () => {
        console.log('Connected to TrackerSpotter');
        updateConnectionStatus(true);
    });
    
    socket.on('disconnect', () => {
        console.log('Disconnected from TrackerSpotter');
        updateConnectionStatus(false);
    });
    
    socket.on('new_announce', (event) => {
        console.log('New announce received:', event);
        handleNewAnnounce(event);
    });
    
    socket.on('logs_cleared', (data) => {
        console.log('Logs cleared:', data);
        allEvents = [];
        filteredEvents = [];
        renderEvents();
        loadStats();
        loadTorrents();  // Reset torrent filter dropdown counts
    });
}

function updateConnectionStatus(connected) {
    const indicator = document.getElementById('statusIndicator');
    const text = document.getElementById('statusText');
    
    if (connected) {
        indicator.classList.add('connected');
        indicator.classList.remove('disconnected');
        text.textContent = 'Connected';
    } else {
        indicator.classList.add('disconnected');
        indicator.classList.remove('connected');
        text.textContent = 'Disconnected';
    }
}

// Load initial data
async function loadInitialData() {
    try {
        await Promise.all([
            loadEvents(),
            loadTorrents(),
            loadStats()
        ]);
    } catch (error) {
        console.error('Error loading initial data:', error);
    }
}

async function loadEvents() {
    try {
        const response = await fetch('/api/events?limit=100');
        const data = await response.json();
        
        if (data.success) {
            allEvents = data.events;
            applyFilters();
        }
    } catch (error) {
        console.error('Error loading events:', error);
    }
}

async function loadTorrents() {
    try {
        const response = await fetch('/api/torrents');
        const data = await response.json();
        
        if (data.success) {
            updateTorrentFilter(data.torrents);
        }
    } catch (error) {
        console.error('Error loading torrents:', error);
    }
}

async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        if (data.success) {
            updateStats(data.stats, data.event_counts);
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Handle new announce from WebSocket
function handleNewAnnounce(event) {
    // Ensure event has required fields
    if (!event.info_hash_hex || !event.timestamp) {
        console.error('Invalid event received:', event);
        return;
    }
    
    // Generate a temporary ID if not present
    if (!event.id) {
        event.id = Date.now() + Math.random();
    }
    
    // Add to beginning of array
    allEvents.unshift(event);
    
    // Cap events in memory to prevent memory issues
    if (allEvents.length > MAX_EVENTS_IN_MEMORY) {
        allEvents = allEvents.slice(0, MAX_EVENTS_IN_MEMORY);
    }
    
    // Apply filters to update the display
    applyFilters();
    
    // Update stats and torrent filter
    loadStats();
    loadTorrents();
    
    // Highlight the new row after rendering
    setTimeout(() => {
        const firstRow = document.querySelector('#eventsTableBody tr:first-child');
        if (firstRow && !firstRow.classList.contains('no-events')) {
            firstRow.classList.add('highlight');
        }
    }, 100);
}

// Filtering
function applyFilters() {
    currentFilters.eventType = document.getElementById('eventFilter').value;
    currentFilters.torrent = document.getElementById('torrentFilter').value;
    currentFilters.search = document.getElementById('searchBox').value.toLowerCase();
    
    filteredEvents = allEvents.filter(event => {
        // Event type filter
        if (currentFilters.eventType !== 'all') {
            const eventType = event.event || 'update';
            if (eventType !== currentFilters.eventType) {
                return false;
            }
        }
        
        // Torrent filter
        if (currentFilters.torrent !== 'all') {
            if (event.info_hash_hex !== currentFilters.torrent) {
                return false;
            }
        }
        
        // Search filter
        if (currentFilters.search) {
            const searchableText = `${event.info_hash_hex} ${event.client_ip} ${event.user_agent || ''}`.toLowerCase();
            if (!searchableText.includes(currentFilters.search)) {
                return false;
            }
        }
        
        return true;
    });
    
    renderEvents();
}

// Rendering
function renderEvents() {
    const tbody = document.getElementById('eventsTableBody');
    
    if (filteredEvents.length === 0) {
        tbody.innerHTML = `
            <tr class="no-events">
                <td colspan="8">
                    <div class="no-events-message">
                        <div class="no-events-icon">📭</div>
                        <h3>No events found</h3>
                        <p>${allEvents.length === 0 ? 
                            'Copy the tracker URL above and add it to your torrent client to start monitoring.' :
                            'Try adjusting your filters or search criteria.'
                        }</p>
                    </div>
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = filteredEvents.map(event => {
        const eventType = event.event || 'update';
        const time = formatTime(event.timestamp);
        const hash = event.info_hash_hex.substring(0, 8) + '...';
        const downloaded = formatBytes(event.downloaded);
        const uploaded = formatBytes(event.uploaded);
        const left = formatBytes(event.left);
        const progress = calculateProgress(event.downloaded, event.left);
        
        // Determine protocol (HTTP if raw_headers exists, otherwise UDP)
        // UDP requests don't have HTTP headers, so raw_headers will be empty
        const isUDP = !event.raw_headers || event.raw_headers === '';
        const protocolBadge = isUDP 
            ? '<span class="protocol-badge udp" title="UDP Protocol">UDP</span>' 
            : '<span class="protocol-badge http" title="HTTP Protocol">HTTP</span>';
        
        return `
            <tr onclick="showEventDetails(${event.id})">
                <td>${time}</td>
                <td>
                    <span class="event-badge ${eventType}">${eventType.toUpperCase()}</span>
                    ${protocolBadge}
                </td>
                <td><span class="torrent-hash" title="${event.info_hash_hex}">${hash}</span></td>
                <td>${event.client_ip}:${event.client_port}</td>
                <td>↓ ${downloaded}</td>
                <td>↑ ${uploaded}</td>
                <td>⏳ ${left}</td>
                <td>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${progress}%"></div>
                    </div>
                    <small>${progress.toFixed(1)}%</small>
                </td>
            </tr>
        `;
    }).join('');
}

function updateStats(stats, eventCounts) {
    document.getElementById('totalEvents').textContent = stats.total_events || 0;
    document.getElementById('uniqueTorrents').textContent = stats.unique_torrents || 0;
    document.getElementById('startedCount').textContent = eventCounts.started || 0;
    document.getElementById('completedCount').textContent = eventCounts.completed || 0;
}

function updateTorrentFilter(torrents) {
    const select = document.getElementById('torrentFilter');
    const currentValue = select.value;
    
    // Keep "All Torrents" option
    select.innerHTML = '<option value="all">All Torrents</option>';
    
    // Add torrent options
    torrents.forEach(torrent => {
        const option = document.createElement('option');
        option.value = torrent.info_hash_hex;
        const shortHash = torrent.info_hash_hex.substring(0, 16) + '...';
        option.textContent = `${shortHash} (${torrent.count})`;
        select.appendChild(option);
    });
    
    // Restore previous selection if still valid
    if (currentValue !== 'all') {
        select.value = currentValue;
    }
}

// Detail Panel
function showEventDetails(eventId) {
    const event = allEvents.find(e => e.id === eventId);
    if (!event) return;
    
    const eventType = event.event || 'update';
    const clientInfo = extractClientInfo(event.user_agent, event.peer_id);
    
    const detailContent = document.getElementById('detailContent');
    detailContent.innerHTML = `
        <div class="detail-section">
            <h4>Event Information</h4>
            <div class="detail-field">
                <div class="detail-label">Timestamp</div>
                <div class="detail-value">${formatFullTimestamp(event.timestamp)}</div>
            </div>
            <div class="detail-field">
                <div class="detail-label">Event Type</div>
                <div class="detail-value"><span class="event-badge ${eventType}">${eventType.toUpperCase()}</span></div>
            </div>
        </div>
        
        <div class="detail-section">
            <h4>Torrent Information</h4>
            <div class="detail-field">
                <div class="detail-label">Info Hash (Hex)</div>
                <div class="detail-value">${event.info_hash_hex}</div>
            </div>
        </div>
        
        <div class="detail-section">
            <h4>Client Information</h4>
            <div class="detail-field">
                <div class="detail-label">IP Address</div>
                <div class="detail-value">${event.client_ip}</div>
            </div>
            <div class="detail-field">
                <div class="detail-label">Port</div>
                <div class="detail-value">${event.client_port}</div>
            </div>
            <div class="detail-field">
                <div class="detail-label">User Agent</div>
                <div class="detail-value">${event.user_agent || 'Not provided'}</div>
            </div>
            <div class="detail-field">
                <div class="detail-label">Peer ID</div>
                <div class="detail-value">${event.peer_id || 'Not provided'}</div>
            </div>
            <div class="detail-field">
                <div class="detail-label">Client Name</div>
                <div class="detail-value">${clientInfo.name} ${clientInfo.version}</div>
            </div>
        </div>
        
        <div class="detail-section">
            <h4>Progress Information</h4>
            <div class="detail-field">
                <div class="detail-label">Downloaded</div>
                <div class="detail-value">${formatBytes(event.downloaded)} (${event.downloaded} bytes)</div>
            </div>
            <div class="detail-field">
                <div class="detail-label">Uploaded</div>
                <div class="detail-value">${formatBytes(event.uploaded)} (${event.uploaded} bytes)</div>
            </div>
            <div class="detail-field">
                <div class="detail-label">Remaining</div>
                <div class="detail-value">${formatBytes(event.left)} (${event.left} bytes)</div>
            </div>
            <div class="detail-field">
                <div class="detail-label">Progress</div>
                <div class="detail-value">${calculateProgress(event.downloaded, event.left).toFixed(2)}%</div>
            </div>
        </div>
        
        <div class="detail-section">
            <h4>Additional Parameters</h4>
            <div class="detail-field">
                <div class="detail-label">Numwant</div>
                <div class="detail-value">${event.numwant || 'Not specified'}</div>
            </div>
            <div class="detail-field">
                <div class="detail-label">Compact</div>
                <div class="detail-value">${event.compact !== null ? event.compact : 'Not specified'}</div>
            </div>
            <div class="detail-field">
                <div class="detail-label">Key</div>
                <div class="detail-value">${event.key || 'Not provided'}</div>
            </div>
        </div>
        
        <div class="detail-section">
            <h4>Raw Query String</h4>
            <div class="detail-field">
                <div class="detail-value raw-data">${escapeHtml(event.raw_query) || 'Not available'}</div>
            </div>
        </div>
        
        <div class="detail-section">
            <h4>Raw HTTP Headers</h4>
            <div class="detail-field">
                <pre class="detail-value raw-data">${escapeHtml(event.raw_headers) || 'Not available (UDP)'}</pre>
            </div>
        </div>
    `;
    
    document.getElementById('detailPanel').classList.add('open');
}

function closeDetailPanel() {
    document.getElementById('detailPanel').classList.remove('open');
}

// Actions
async function refreshEvents() {
    await loadInitialData();
}

async function exportCSV() {
    try {
        window.location.href = '/api/export/csv';
    } catch (error) {
        console.error('Error exporting CSV:', error);
        alert('Failed to export CSV');
    }
}

async function exportJSON() {
    try {
        window.location.href = '/api/export/json';
    } catch (error) {
        console.error('Error exporting JSON:', error);
        alert('Failed to export JSON');
    }
}

async function clearLogs() {
    if (!confirm('Are you sure you want to clear all logs? This cannot be undone.')) {
        return;
    }
    
    try {
        const response = await fetch('/api/clear', { method: 'POST' });
        const data = await response.json();
        
        if (data.success) {
            console.log(`Cleared ${data.deleted} events`);
            allEvents = [];
            filteredEvents = [];
            renderEvents();
            await loadStats();
        } else {
            alert('Failed to clear logs: ' + data.error);
        }
    } catch (error) {
        console.error('Error clearing logs:', error);
        alert('Failed to clear logs');
    }
}

function copyTrackerUrl(type = 'http') {
    let url;
    let label;
    
    switch(type) {
        case 'http':
            url = document.getElementById('trackerUrlHttp').textContent;
            label = 'HTTP (local)';
            break;
        case 'http-docker':
            url = document.getElementById('trackerUrlHttpDocker').textContent;
            label = 'HTTP (Docker)';
            break;
        case 'udp':
            url = document.getElementById('trackerUrlUdp').textContent;
            label = 'UDP (local)';
            break;
        case 'udp-docker':
            url = document.getElementById('trackerUrlUdpDocker').textContent;
            label = 'UDP (Docker)';
            break;
        case 'http-ipv6':
            url = document.getElementById('trackerUrlHttpIpv6').textContent;
            label = 'HTTP (IPv6)';
            break;
        case 'udp-ipv6':
            url = document.getElementById('trackerUrlUdpIpv6').textContent;
            label = 'UDP (IPv6)';
            break;
        default:
            url = document.getElementById('trackerUrlHttp').textContent;
            label = 'HTTP';
    }
    
    navigator.clipboard.writeText(url).then(() => {
        alert(`${label} tracker URL copied to clipboard!`);
    }).catch(err => {
        console.error('Failed to copy:', err);
    });
}

function closeBanner() {
    document.getElementById('quickStartBanner').style.display = 'none';
}

// Utility functions
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatBytes(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatTime(timestamp) {
    const date = new Date(timestamp);
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
    const ms = String(date.getMilliseconds()).padStart(3, '0');
    return `${hours}:${minutes}:${seconds}.${ms}`;
}

function formatFullTimestamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString();
}

function calculateProgress(downloaded, left) {
    const total = downloaded + left;
    if (total === 0) return left === 0 ? 100 : 0;
    return (downloaded / total) * 100;
}

function extractClientInfo(userAgent, peerId) {
    // Simple client detection from user agent
    if (userAgent && userAgent.includes('/')) {
        const parts = userAgent.split('/');
        return {
            name: parts[0],
            version: parts[1] ? parts[1].split(' ')[0] : ''
        };
    }
    
    // Try to detect from peer ID
    if (peerId && peerId.length >= 8) {
        try {
            const clientCode = peerId.substring(0, 8);
            const clients = {
                '2d71423': 'qBittorrent',
                '2d5452': 'Transmission',
                '2d5554': 'μTorrent',
                '2d4445': 'Deluge'
            };
            
            for (const [code, name] of Object.entries(clients)) {
                if (clientCode.startsWith(code)) {
                    return { name, version: '' };
                }
            }
        } catch (e) {
            // Ignore parsing errors
        }
    }
    
    return { name: 'Unknown', version: '' };
}

function setupEventListeners() {
    // Close detail panel when clicking outside
    document.addEventListener('click', (e) => {
        const panel = document.getElementById('detailPanel');
        if (panel.classList.contains('open') && !panel.contains(e.target) && 
            !e.target.closest('.events-table')) {
            closeDetailPanel();
        }
    });
    
    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Escape to close detail panel
        if (e.key === 'Escape') {
            closeDetailPanel();
        }
        
        // Ctrl+R or F5 to refresh
        if ((e.ctrlKey && e.key === 'r') || e.key === 'F5') {
            e.preventDefault();
            refreshEvents();
        }
    });
}

