# PI-HOLE-BLOCK

A collection of blocklists for Pi-hole DNS server.

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