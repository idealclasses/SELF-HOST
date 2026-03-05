#!/usr/bin/env python3

import urllib.request
import re

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
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as res:
                code = res.getcode()
                return 200 <= code < 300
        except:
            return False

def fetch_m3u(url):
    """Fetch M3U from URL"""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as res:
            return res.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return None

def parse_m3u(content):
    """Parse M3U content"""
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
                if url and not url.startswith('#'):
                    channels.append({'extinf': extinf, 'url': url})
        i += 1
    return channels

def add_working_channels():
    """Fetch from new source and add working channels"""
    source_url = "https://raw.githubusercontent.com/saifujjaman/bd-iptv/master/iptv-list.m3u"
    
    print(f"Fetching from: {source_url}")
    content = fetch_m3u(source_url)
    
    if content is None:
        print("Failed to fetch source")
        return
    
    channels = parse_m3u(content)
    print(f"Found {len(channels)} channels in source")
    
    # Read existing channels
    with open('/workspaces/PI-HOLE-BLOCK/working_channels/BD_channels.m3u', 'r', encoding='utf-8', errors='ignore') as f:
        existing = f.read()
    
    working_count = 0
    added = 0
    
    # Check each channel and add if working
    for i, ch in enumerate(channels):
        url = ch['url']
        extinf = ch['extinf']
        
        print(f"[{i+1}/{len(channels)}] Checking: {url[:80]}...")
        
        if check_url(url):
            working_count += 1
            print(f"  ✅ Working!")
            
            # Check if already in playlist
            if url not in existing:
                # Update group-title to "Working Channels"
                updated_extinf = re.sub(
                    r'group-title="[^"]*"',
                    'group-title="Working Channels"',
                    extinf
                )
                if 'group-title' not in extinf:
                    updated_extinf = extinf.replace('#EXTINF:', '#EXTINF:-1 group-title="Working Channels"')
                
                # Append to file
                with open('/workspaces/PI-HOLE-BLOCK/working_channels/BD_channels.m3u', 'a', encoding='utf-8') as f:
                    f.write(updated_extinf + '\n')
                    f.write(url + '\n')
                
                added += 1
                print(f"  ➕ Added to playlist")
        else:
            print(f"  ❌ Not working")
    
    print(f"\n✅ Complete!")
    print(f"Checked: {len(channels)} channels")
    print(f"Working: {working_count} channels")
    print(f"Added: {added} new channels to BD_channels.m3u")

if __name__ == "__main__":
    add_working_channels()
