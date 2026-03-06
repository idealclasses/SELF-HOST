#!/usr/bin/env python3
import urllib.request
import re
from urllib.error import URLError
import time

# List of external blocklists to download
BLOCKLISTS = [
    ("Steven Black", "https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts"),
    ("Malware.Expert", "https://malware.expert/downloads/domains/index.txt"),
    ("PiHole Malware", "https://raw.githubusercontent.com/notracking/hosts-blocklists/master/malware/hosts"),
    ("Gambling Domains", "https://raw.githubusercontent.com/pihole/pihole-regex/master/regex.list"),
    ("Phishing Army", "https://phishing.army/download/phishing_army_blocklist_extended.txt"),
    ("URLhaus", "https://urlhaus-api.abuse.ch/downloads/csv_recent/"),
    ("OpenPhish", "https://openphish.com/feed.txt"),
]

def download_blocklist(name, url):
    """Download and parse a blocklist from URL"""
    domains = set()
    try:
        print(f"  Downloading {name}...")
        with urllib.request.urlopen(url, timeout=10) as response:
            content = response.read().decode('utf-8', errors='ignore')
        print(f"  ✓ Downloaded {len(content)} bytes from {name}")
        
        for line in content.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Parse different formats
            parts = line.split()
            if len(parts) >= 2:
                if parts[0] in ['0.0.0.0', '127.0.0.1']:
                    # hosts file format
                    domain = parts[1]
                elif parts[0].startswith('^'):
                    # regex format, skip
                    continue
                else:
                    domain = parts[0]
            else:
                domain = parts[0] if parts else ""
            
            if domain and '.' in domain:
                domains.add(domain.lower())
        
        print(f"  ✓ Extracted {len(domains)} domains from {name}")
        return domains
    except URLError as e:
        print(f"  ✗ Failed to download {name}: {e}")
        return set()
    except Exception as e:
        print(f"  ✗ Error processing {name}: {e}")
        return set()

print("=" * 60)
print("PI-HOLE COMPREHENSIVE BLOCKLIST MERGER")
print("=" * 60)

# Download all blocklists
all_external_domains = set()
for name, url in BLOCKLISTS:
    domains = download_blocklist(name, url)
    all_external_domains.update(domains)
    time.sleep(1)  # Rate limiting

print(f"\n✓ Total domains from external sources: {len(all_external_domains)}")

# Read current blocklist
current_domains = set()
current_comments = []
try:
    with open('youtube-blocklist.txt', 'r') as f:
        for line in f:
            line_stripped = line.strip()
            if line_stripped.startswith('#'):
                continue
            elif line_stripped:
                current_domains.add(line_stripped.lower())
    print(f"✓ Read {len(current_domains)} domains from current blocklist")
except Exception as e:
    print(f"✗ Error reading current blocklist: {e}")

# Merge and sort
all_domains = sorted(all_external_domains | current_domains)
print(f"\n✓ TOTAL unique domains after merge: {len(all_domains)}")

# Write merged blocklist
header = f"""# COMPREHENSIVE PI-HOLE BLOCKLIST
# ====================================
# This blocklist is designed to block as much as possible including:
# - Malware & Phishing
# - Ads, Trackers & Analytics
# - Gambling & Betting
# - Streaming Services
# - Social Media
# - File Sharing & Torrents
# - VPN & Proxy services
# - Bypass techniques
#
# Merged from:
# - Original YouTube/Malware blocklist
# - Steven Black hosts file
# - Malware.Expert database
# - PiHole Malware list
# - Phishing Army
# - URLhaus
# - OpenPhish
# 
# Total unique domains: {len(all_domains)}
# Last updated: 2026-01-21

"""

try:
    with open('youtube-blocklist.txt', 'w') as f:
        f.write(header)
        f.write("# ===== COMBINED DOMAIN LIST =====\n\n")
        for domain in all_domains:
            f.write(domain + '\n')
    
    print("\n" + "=" * 60)
    print(f"✓ Successfully merged blocklists!")
    print(f"✓ Blocklist size: {len(all_domains)} domains")
    print(f"✓ File: youtube-blocklist.txt")
    print("=" * 60)
except Exception as e:
    print(f"\n✗ Error writing blocklist: {e}")


