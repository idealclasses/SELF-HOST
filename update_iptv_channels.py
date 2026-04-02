#!/usr/bin/env python3
import requests
import re
from pathlib import Path
import time

# New IPTV links to check
NEW_LINKS = [
    "https://is.gd/ugCCtg.m3u",
    "https://is.gd/SvojrE.m3u",
    "https://bdix-iptv.netlify.app/iptv.m3u",
    "https://raw.githubusercontent.com/ar-rony/smartiptv-playlist/master/MYIPTVLIST.m3u",
    "https://raw.githubusercontent.com/sydul104/main04/refs/heads/main/my"
]

WORKING_CHANNELS_DIR = Path("working_channels")
BD_CHANNELS_FILE = WORKING_CHANNELS_DIR / "BD_channels.m3u"
ANIMATION_FILE = WORKING_CHANNELS_DIR / "animation.m3u"

def fetch_m3u_content(url):
    """Fetch m3u content from URL"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"❌ Failed to fetch {url}: {e}")
        return None

def parse_m3u(content):
    """Parse m3u content and return list of channels"""
    channels = []
    lines = content.strip().split('\n')

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if line.startswith('#EXTINF:'):
            extinf = line
            # Get next non-empty line as URL
            i += 1
            while i < len(lines) and not lines[i].strip():
                i += 1

            if i < len(lines):
                url = lines[i].strip()
                if url and not url.startswith('#'):
                    channels.append({
                        'extinf': extinf,
                        'url': url
                    })
        i += 1

    return channels


def categorize_channel(channel_info):
    """Categorize channel as BD or Animation or other"""
    extinf = channel_info['extinf'].lower()
    title = channel_info.get('title', '').lower()

    animation_keywords = ['anim', 'cartoon', 'kids', 'children']
    bd_keywords = ['bd', 'bangla', 'bangladesh', 'dhaka']

    for keyword in animation_keywords:
        if keyword in extinf or keyword in title:
            return 'animation'

    for keyword in bd_keywords:
        if keyword in extinf or keyword in title:
            return 'bd'

    return 'other'

def extract_channel_title(extinf):
    """Extract channel title from EXTINF line"""
    match = re.search(r',([^,]+)$', extinf)
    if match:
        return match.group(1).strip()
    return "Unknown"

def add_channels_to_m3u(channels, m3u_file, category):
    """Add new channels to m3u file"""
    if not channels:
        return 0

    try:
        # Read existing content
        content = ""
        if m3u_file.exists():
            with open(m3u_file, 'r', encoding='utf-8') as f:
                content = f.read()

        # Ensure it has header
        if not content.startswith('#EXTM3U'):
            content = "#EXTM3U\n" + content

        # Remove trailing newline
        content = content.rstrip('\n')

        added_count = 0
        for channel in channels:
            # Add newline and channel info
            content += "\n" + channel['extinf'] + "\n" + channel['url']
            added_count += 1

        # Write back
        with open(m3u_file, 'w', encoding='utf-8') as f:
            f.write(content + "\n")

        return added_count
    except Exception as e:
        print(f"Error writing to {m3u_file}: {e}")
        return 0

def main():
    print("🔍 IPTV Channel Update Tool")
    print(f"{'='*50}")
    print(f"Checking {len(NEW_LINKS)} new IPTV sources...\n")

    all_new_channels = []

    for link in NEW_LINKS:
        print(f"📥 Fetching: {link}")
        content = fetch_m3u_content(link)

        if not content:
            continue

        channels = parse_m3u(content)
        print(f"   Found {len(channels)} channels")

        # Add all channels (including duplicates)
        for ch in channels:
            title = extract_channel_title(ch['extinf'])
            category = categorize_channel({'extinf': ch['extinf'], 'title': title})
            ch['category'] = category
            ch['title'] = title
            all_new_channels.append(ch)

        time.sleep(0.5)  # Rate limiting

    print(f"\n✨ Found {len(all_new_channels)} total channels")
    print(f"{'='*50}\n")

    # Categorize and add channels
    bd_channels = [ch for ch in all_new_channels if ch['category'] == 'bd']
    anim_channels = [ch for ch in all_new_channels if ch['category'] == 'animation']
    other_channels = [ch for ch in all_new_channels if ch['category'] == 'other']

    # Add BD channels
    if bd_channels:
        added = add_channels_to_m3u(bd_channels, BD_CHANNELS_FILE, 'bd')
        print(f"✅ Added {added} BD channels to {BD_CHANNELS_FILE}")

    # Add Animation channels
    if anim_channels:
        added = add_channels_to_m3u(anim_channels, ANIMATION_FILE, 'animation')
        print(f"✅ Added {added} Animation channels to {ANIMATION_FILE}")

    # Show other channels for manual review
    if other_channels:
        print(f"\n⚠️  Other Channels ({len(other_channels)}) - Review manually:")
        for ch in other_channels[:10]:
            print(f"  - {ch['title']}")
        if len(other_channels) > 10:
            print(f"  ... and {len(other_channels) - 10} more")

    print(f"\n{'='*50}")
    print("✨ Update complete!")

if __name__ == "__main__":
    main()
