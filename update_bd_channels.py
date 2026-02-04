#!/usr/bin/env python3

import urllib.request

# Download the playlist
url = "https://github.com/abusaeeidx/Mrgify-BDIX-IPTV/raw/main/playlist.m3u"
response = urllib.request.urlopen(url)
data = response.read().decode('utf-8')
lines = data.split('\n')

# Extract BD channels
bd_entries = []
i = 0
while i < len(lines):
    line = lines[i].strip()
    if line.startswith('#EXTINF') and 'BD' in line:
        # Collect the entry: #EXTINF line and the next URL line
        entry = [line + '\n']
        i += 1
        if i < len(lines):
            entry.append(lines[i].strip() + '\n')
        bd_entries.append(''.join(entry))
    i += 1

# Make unique based on channel name
unique_bd = {}
for entry in bd_entries:
    # Extract channel name from #EXTINF line
    extinf_line = entry.split('\n')[0]
    # Find the last comma and take after it
    comma_index = extinf_line.rfind(',')
    if comma_index != -1:
        channel_name = extinf_line[comma_index + 1:].strip()
        if channel_name not in unique_bd:
            unique_bd[channel_name] = entry

# Print the unique BD channel entries
print('#EXTM3U')
for entry in unique_bd.values():
    print(entry.strip())

# Now, read existing BD_channels.m3u
with open('/workspaces/PI-HOLE-BLOCK/BD_channels.m3u', 'r') as f:
    existing_lines = f.readlines()

# Parse existing entries
existing_channels = {}
i = 0
while i < len(existing_lines):
    line = existing_lines[i].strip()
    if line.startswith('#EXTINF'):
        extinf_line = line
        i += 1
        url_line = existing_lines[i].strip() if i < len(existing_lines) else ''
        # Extract channel name
        comma_index = extinf_line.rfind(',')
        if comma_index != -1:
            channel_name = extinf_line[comma_index + 1:].strip()
            existing_channels[channel_name] = extinf_line + '\n' + url_line + '\n'
    i += 1

# Merge: add new ones if not present
for name, entry in unique_bd.items():
    if name not in existing_channels:
        existing_channels[name] = entry

# Write back to BD_channels.m3u
with open('/workspaces/PI-HOLE-BLOCK/BD_channels.m3u', 'w') as f:
    f.write('#EXTM3U\n')
    for entry in existing_channels.values():
        f.write(entry)