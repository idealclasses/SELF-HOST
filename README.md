# PI-HOLE-BLOCK

A collection of blocklists for Pi-hole DNS server and IPTV playlists.

## YouTube Complete Blocker

### Features
- Blocks all YouTube.com domains and subdomains
- Blocks YouTube Shorts
- Blocks YouTube Music
- Blocks YouTube Gaming
- Blocks YouTube Kids
- Blocks youtu.be shortlinks
- Blocks YouTube embeds (youtube-nocookie.com)
- Blocks related CDN and analytics domains

### How to Use

1. Open your Pi-hole admin panel (usually `http://pi.hole/admin`)
2. Go to **Adlists** (Settings > Adlists)
3. Copy the contents of `youtube-blocklist.txt` or use the raw URL
4. Paste into the "Address (URL or file path)" field
5. Click "Add"
6. Update gravity: **Tools > Update Gravity**

### Alternative: Direct URL Method
If hosting this file online, you can add directly:
```
https://raw.githubusercontent.com/yourusername/PI-HOLE-BLOCK/main/youtube-blocklist.txt
```

### What Gets Blocked
- Direct YouTube access (youtube.com, youtu.be)
- YouTube embeds on other websites
- YouTube mobile apps (will fail to load)
- YouTube Shorts, Music, Gaming, Kids sections
- YouTube Studio and creator tools
- Video upload services

### Note
⚠️ **Warning**: Blocking Google domains broadly may affect other Google services. If you only want to block YouTube without affecting Gmail, Google Search, etc., edit the blocklist to remove or comment out wildcard Google domain entries.

## Bangladesh (BD) IPTV Channels Playlist

### Overview
A curated M3U playlist containing Bangladesh (BD) channels extracted from YouTube live streams and other IPTV sources.

### Features
- 78 unique Bangladesh channels
- Channels from news, entertainment, and other categories
- M3U format compatible with most IPTV players
- Regularly updated with fresh sources

### Channel List
The playlist includes channels such as:
- BD | EKHON TV
- BD | Channel 24
- BD | Ekattor TV
- BD | Independent Television
- BD | DBC News
- BD | NEWS24 Television
- BD | ATN News
- BD | SOMOY NEWS
- BD | News
- And 69+ additional BD channels from various sources

### How to Use

1. Download the `BD_channels.m3u` file or use the raw URL
2. Open in your preferred IPTV player (VLC, Kodi, etc.)
3. Load the playlist and enjoy BD channels

### Direct URL Method
```
https://raw.githubusercontent.com/idealclasses/PI-HOLE-BLOCK/main/BD_channels.m3u
```

### Sources
- Primary: YouTube IPTV playlist (time2shine/IPTV)
- Secondary: BDIX IPTV playlist (abusaeeidx/Mrgify-BDIX-IPTV)

### Note
⚠️ **Important**: These are YouTube-based live streams that may require:
- A compatible media player that supports YouTube HLS
- VPN access if geo-restricted
- The URLs are temporary and may expire - refresh the playlist periodically

### Recent Updates
- **v1.0**: Initial BD channels extraction (9 channels from YouTube source)
- **v1.1**: Combined with additional BD channels (78 total unique channels from multiple sources)