#!/usr/bin/env python3

import urllib.request
import socket
from urllib.error import URLError, HTTPError
import time

USER_AGENT = 'Mozilla/5.0 (compatible; IPTV-CHECKER/1.0)'
TIMEOUT = 5

def check_url(url):
    """Check if URL is accessible"""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT}, method='HEAD')
        with urllib.request.urlopen(req, timeout=TIMEOUT) as res:
            code = res.getcode()
            return 200 <= code < 300
    except Exception:
        # Try GET if HEAD fails
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as res:
                code = res.getcode()
                return 200 <= code < 300
        except:
            return False

def fetch_playlist(url):
    """Fetch M3U playlist from URL"""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
            return response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return None

def parse_m3u(content):
    """Parse M3U playlist content"""
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
                    channels.append({'name': name, 'url': url, 'extinf': extinf})
        i += 1
    return channels

# Main
print("=" * 80)
print("IPTV CHANNEL LINK VERIFICATION")
print("=" * 80)

upstream_sources = [
    "https://github.com/abusaeeidx/Mrgify-BDIX-IPTV/raw/main/playlist.m3u",
    "https://raw.githubusercontent.com/time2shine/IPTV/refs/heads/master/combined.m3u",
    "https://raw.githubusercontent.com/time2shine/IPTV/main/playlist.m3u",
    "https://private-zone-by-xfireflix.pages.dev/playlist-isp-bdix.m3u",
]

print("\nFetching and checking upstream IPTV sources...\n")

all_channels = {}
for source_url in upstream_sources:
    print(f"📡 Source: {source_url}")
    content = fetch_playlist(source_url)
    
    if content is None:
        print(f"  ❌ Failed to fetch\n")
        continue
    
    channels = parse_m3u(content)
    print(f"  Found {len(channels)} channels")
    
    working = 0
    dead = 0
    
    for ch in channels[:10]:  # Check first 10 channels per source
        is_working = check_url(ch['url'])
        status = "✅" if is_working else "❌"
        
        if ch['name'] not in all_channels:
            all_channels[ch['name']] = {
                'url': ch['url'],
                'extinf': ch['extinf'],
                'working': is_working
            }
            
            if is_working:
                print(f"    {status} {ch['name']}")
                working += 1
            else:
                print(f"    {status} {ch['name']} (DEAD)")
                dead += 1
        
        time.sleep(0.2)
    
    print(f"  Summary: {working} working, {dead} dead\n")
    time.sleep(1)

# Check current BD_channels.m3u
print("\n" + "=" * 80)
print("CURRENT BD_CHANNELS STATUS")
print("=" * 80 + "\n")

current_channels = []
with open('/workspaces/PI-HOLE-BLOCK/BD_channels.m3u', 'r') as f:
    content = f.read()
    current_channels = parse_m3u(content)

print(f"Total channels in BD_channels.m3u: {len(current_channels)}")

# Check status of current channels
working_count = 0
dead_count = 0
checked = 0

print("\nChecking current channel URLs (first 30)...\n")
for ch in current_channels[:30]:
    checked += 1
    is_working = check_url(ch['url'])
    status = "✅" if is_working else "❌"
    
    if is_working:
        working_count += 1
        print(f"{status} {ch['name']}")
    else:
        dead_count += 1
        print(f"{status} {ch['name']} (URL DEAD)")
    
    time.sleep(0.2)

print(f"\n{'=' * 80}")
print(f"Quick Check Results (first {checked} channels):")
print(f"  ✅ Working: {working_count}")
print(f"  ❌ Dead: {dead_count}")
print(f"  Success Rate: {(working_count/checked*100):.1f}%")
print(f"{'=' * 80}\n")

# Summary
print("RECOMMENDATIONS:")
print("1. The upstream sources have fresh/updated channel links")
print("2. Many current channels in BD_channels.m3u appear to be dead")
print("3. Consider running 'python3 update_bd_channels.py' to refresh from upstream")
print("4. Add new sources if available:\n")

for source in upstream_sources:
    print(f"   - {source}")
