#!/usr/bin/env python3

import urllib.request
import socket
from urllib.error import URLError, HTTPError

# Source for animation channels
SOURCE = "https://iptv-org.github.io/iptv/categories/animation.m3u"

USER_AGENT = 'Mozilla/5.0 (compatible; PI-HOLE-BLOCK/1.0)'
TIMEOUT = 6


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as res:
        return res.read().decode('utf-8', errors='ignore')


def parse_entries(data):
    lines = data.split('\n')
    entries = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('#EXTINF'):
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


# Fetch animation entries
try:
    data = fetch(SOURCE)
    entries = parse_entries(data)
    print(f"Fetched {len(entries)} animation entries from {SOURCE}")
except Exception as e:
    print(f"Failed to fetch {SOURCE}: {e}")
    exit(1)

# Check liveliness
working_entries = []
for entry in entries:
    parts = entry.strip().split('\n')
    if len(parts) < 2:
        continue
    url = parts[1].strip()
    name = channel_name_from_extinf(parts[0])
    print(f"Checking: {name} -> {url}")
    if is_url_working(url):
        print("  ✅ OK"
        working_entries.append(entry)
    else:
        print("  ⚠️ Failed"

# Write to animation.m3u
with open('/workspaces/PI-HOLE-BLOCK/animation.m3u', 'w') as f:
    f.write('#EXTM3U\n')
    for entry in working_entries:
        f.write(entry)

print(f"Wrote {len(working_entries)} working animation channels to animation.m3u")
