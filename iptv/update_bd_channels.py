#!/usr/bin/env python3

import urllib.request
import socket
from urllib.error import URLError, HTTPError

# List of upstream playlist sources to pull BD channels from
SOURCES = [
    "https://github.com/abusaeeidx/Mrgify-BDIX-IPTV/raw/main/playlist.m3u",
    "https://private-zone-by-xfireflix.pages.dev/playlist-isp-bdix.m3u",
]

USER_AGENT = 'Mozilla/5.0 (compatible; PI-HOLE-BLOCK/1.0)'
TIMEOUT = 6


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as res:
        return res.read().decode('utf-8', errors='ignore')


def parse_bd_entries(data, include_all=False):
    lines = data.split('\n')
    entries = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('#EXTINF') and (include_all or 'BD' in line):
            entry = [line + '\n']
            i += 1
            if i < len(lines):
                entry.append(lines[i].strip() + '\n')
            entries.append(''.join(entry))
        i += 1
    return entries


def channel_name_from_extinf(extinf_line):
    comma_index = extinf_line.rfind(',')
    if comma_index != -1:
        return extinf_line[comma_index + 1:].strip()
    return extinf_line


def is_url_working(url):
    # Try HEAD first; fall back to small GET if HEAD fails
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT}, method='HEAD')
        with urllib.request.urlopen(req, timeout=TIMEOUT) as res:
            code = res.getcode()
            if 200 <= code < 300:
                return True
    except Exception:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as res:
                code = res.getcode()
                try:
                    _ = res.read(1024)
                except Exception:
                    pass
                if 200 <= code < 300:
                    return True
        except (HTTPError, URLError, socket.timeout, ValueError):
            return False
    return False


# Collect BD entries from all sources
all_entries = []
for src in SOURCES:
    try:
        data = fetch(src)
        include_all = 'private-zone-by-xfireflix.pages.dev' in src or 'playlist-isp-bdix' in src
        entries = parse_bd_entries(data, include_all=include_all)
        kind = 'all' if include_all else 'BD'
        print(f"Fetched {len(entries)} {kind} entries from {src}")
        if len(entries) == 0:
            snippet = data.strip().splitlines()[:15]
            print(f"  Sample lines from {src}:")
            for ln in snippet:
                print("   ", ln)
        all_entries.extend(entries)
    except Exception as e:
        print(f"Failed to fetch {src}: {e}")

# Make unique by channel name (prefer first occurrence)
unique_bd = {}
for entry in all_entries:
    extinf_line = entry.split('\n')[0]
    name = channel_name_from_extinf(extinf_line)
    if name not in unique_bd:
        unique_bd[name] = entry

# Print summary of found unique channels
print('#EXTM3U')
for entry in unique_bd.values():
    print(entry.strip())

# Check URL liveliness and filter to working ones
working_bd = {}
for name, entry in unique_bd.items():
    parts = entry.strip().split('\n')
    if len(parts) < 2:
        continue
    url = parts[1].strip()
    print(f"Checking: {name} -> {url}")
    if is_url_working(url):
        print(f"  ✅ OK: {name}")
        working_bd[name] = entry
    else:
        print(f"  ⚠️ Failed: {name}")

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

# Merge: add new working ones if not present
for name, entry in working_bd.items():
    if name not in existing_channels:
        existing_channels[name] = entry

# Write back to BD_channels.m3u
with open('/workspaces/PI-HOLE-BLOCK/BD_channels.m3u', 'w') as f:
    f.write('#EXTM3U\n')
    for entry in existing_channels.values():
        f.write(entry)