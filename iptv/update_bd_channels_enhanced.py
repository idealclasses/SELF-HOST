#!/usr/bin/env python3
"""
Enhanced BD Channels Update Script
Fetches and validates IPTV channels from upstream sources
"""

import urllib.request
import socket
from urllib.error import URLError, HTTPError
import time

USER_AGENT = 'Mozilla/5.0 (compatible; PI-HOLE-BLOCK/1.0)'
TIMEOUT = 6

# Upstream sources prioritized by reliability
SOURCES = [
    ("xfireflix BDIX", "https://private-zone-by-xfireflix.pages.dev/playlist-isp-bdix.m3u", True),
    ("Mrgify BDIX", "https://github.com/abusaeeidx/Mrgify-BDIX-IPTV/raw/main/playlist.m3u", False),
    ("time2shine combined", "https://raw.githubusercontent.com/time2shine/IPTV/refs/heads/master/combined.m3u", True),
]

def fetch(url):
    """Download content from URL"""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as res:
            return res.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return None

def parse_m3u(content):
    """Parse M3U playlist format"""
    channels = []
    lines = content.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('#EXTINF'):
            extinf = line
            i += 1
            if i < len(lines):
                url = lines[i].strip()
                # Extract channel name
                comma_idx = extinf.rfind(',')
                if comma_idx != -1:
                    name = extinf[comma_idx + 1:].strip()
                    if name and url:
                        channels.append({
                            'name': name,
                            'url': url,
                            'extinf': extinf
                        })
        i += 1
    return channels

def is_url_working(url):
    """Test if stream URL is accessible"""
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
                except:
                    pass
                if 200 <= code < 300:
                    return True
        except (HTTPError, URLError, socket.timeout, ValueError):
            return False
    return False

print("=" * 70)
print("BD CHANNELS UPDATE - VERIFICATION & REFRESH")
print("=" * 70)

# Collect channels from all sources
all_channels = {}
for source_name, source_url, include_all in SOURCES:
    print(f"\n📡 Fetching from {source_name}...")
    data = fetch(source_url)
    
    if data is None:
        print(f"   ❌ Failed to fetch")
        continue
    
    channels = parse_m3u(data)
    print(f"   Found {len(channels)} channels")
    
    working = 0
    dead = 0
    
    # Check channels and add if not duplicate
    for ch in channels:
        if ch['name'] not in all_channels:
            is_working = is_url_working(ch['url'])
            
            if is_working:
                all_channels[ch['name']] = ch
                working += 1
                print(f"   ✅ {ch['name']}")
                
                # Limit verification for speed
                if working >= 20:
                    print(f"   ... (skipping further checks from this source)")
                    working = -1  # Mark as limited
                    break
            else:
                dead += 1
        
        time.sleep(0.1)
    
    if working > 0:
        print(f"   ✓ Added {working} working channels")
    
    time.sleep(0.5)

print(f"\n{'=' * 70}")
print(f"Total unique working channels collected: {len(all_channels)}")
print(f"{'=' * 70}\n")

# Read existing BD_channels.m3u
existing_channels = {}
try:
    with open('BD_channels.m3u', 'r') as f:
        lines = f.readlines()
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('#EXTINF'):
            extinf = line
            i += 1
            if i < len(lines):
                url = lines[i].strip()
                comma_idx = extinf.rfind(',')
                if comma_idx != -1:
                    name = extinf[comma_idx + 1:].strip()
                    existing_channels[name] = {'extinf': extinf, 'url': url}
        i += 1
    
    print(f"Current BD_channels.m3u: {len(existing_channels)} channels")
except Exception as e:
    print(f"Error reading existing file: {e}")

# Merge: keep existing working ones, add new ones
merged = dict(existing_channels)
new_count = 0
for name, ch in all_channels.items():
    if name not in merged:
        merged[name] = ch
        new_count += 1

print(f"New channels to add: {new_count}")
print(f"Final merged count: {len(merged)}\n")

# Write updated playlist
print("Writing to BD_channels.m3u...")
with open('BD_channels.m3u', 'w') as f:
    f.write('#EXTM3U\n')
    for name, ch in sorted(merged.items()):
        f.write(f"{ch['extinf']}\n")
        f.write(f"{ch['url']}\n")

print("✅ BD_channels.m3u updated successfully!")
print(f"   Total channels: {len(merged)}")
print(f"{'=' * 70}\n")
