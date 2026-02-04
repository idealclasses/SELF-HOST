#!/usr/bin/env python3
import urllib.request
import re

# List of playlist URLs
urls = [
    "https://github.com/abusaeeidx/Mrgify-BDIX-IPTV/raw/main/playlist.m3u",
    "https://raw.githubusercontent.com/time2shine/IPTV/refs/heads/master/combined.m3u"
]

all_bd_entries = []

for url in urls:
    try:
        response = urllib.request.urlopen(url)
        new_playlist = response.read().decode('utf-8')
    except:
        continue

    # Extract BD channels from new playlist
    lines = new_playlist.split('\n')
    bd_entries = []
    current_entry = []
    for line in lines:
        if line.startswith('#EXTINF') and 'BD' in line:
            if current_entry:
                bd_entries.append('\n'.join(current_entry))
            current_entry = [line]
        elif current_entry and line.startswith('http'):
            current_entry.append(line)
            bd_entries.append('\n'.join(current_entry))
            current_entry = []

    all_bd_entries.extend(bd_entries)

# Read existing BD channels
with open('/workspaces/PI-HOLE-BLOCK/BD_channels.m3u', 'r') as f:
    existing = f.read()

# Combine and deduplicate
existing_lines = existing.split('\n')
combined = ['#EXTM3U']
existing_channels = set()
for i in range(1, len(existing_lines), 2):
    if i+1 < len(existing_lines):
        channel = existing_lines[i]
        url = existing_lines[i+1]
        if channel.startswith('#EXTINF'):
            # Extract channel name
            match = re.search(r',(.+)$', channel)
            if match:
                name = match.group(1).strip()
                if 'BD' in name:
                    existing_channels.add(name)
                    combined.extend([channel, url])

for entry in all_bd_entries:
    parts = entry.split('\n')
    if len(parts) == 2:
        channel_name = parts[0].split(',')[-1].strip()
        if channel_name not in existing_channels:
            combined.extend(parts)
            existing_channels.add(channel_name)

# Write back
with open('/workspaces/PI-HOLE-BLOCK/BD_channels.m3u', 'w') as f:
    f.write('\n'.join(combined))