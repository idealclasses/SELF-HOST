#!/usr/bin/env python3
import urllib.request
import re

print("Downloading Steven Black hosts file...")
url = "https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts"

try:
    with urllib.request.urlopen(url) as response:
        content = response.read().decode('utf-8')
    print(f"Downloaded {len(content)} bytes")
except Exception as e:
    print(f"Error downloading: {e}")
    exit(1)

# Extract domains from hosts file format (0.0.0.0 or 127.0.0.1)
steven_domains = set()
for line in content.split('\n'):
    line = line.strip()
    if line and not line.startswith('#'):
        parts = line.split()
        if len(parts) >= 2:
            if parts[0] in ['0.0.0.0', '127.0.0.1']:
                steven_domains.add(parts[1])

print(f"Extracted {len(steven_domains)} unique domains from Steven Black")

# Read current blocklist
current_domains = set()
current_comments = []
try:
    with open('youtube-blocklist.txt', 'r') as f:
        for line in f:
            line_stripped = line.strip()
            if line_stripped.startswith('#'):
                current_comments.append(line_stripped)
            elif line_stripped:
                current_domains.add(line_stripped)
    print(f"Read {len(current_domains)} current domains")
except Exception as e:
    print(f"Error reading current blocklist: {e}")

# Merge and sort
all_domains = sorted(steven_domains | current_domains)
print(f"Total unique domains after merge: {len(all_domains)}")

# Write merged blocklist
header = f"""# Comprehensive Pi-hole Blocklist
# Merged from:
# - Original YouTube/Malware blocklist (youtube-blocklist.txt)
# - Steven Black hosts file (https://github.com/StevenBlack/hosts)
# 
# Total unique domains: {len(all_domains)}
# Last updated: 2026-01-21

"""

with open('youtube-blocklist.txt', 'w') as f:
    f.write(header)
    f.write("# ===== Combined Domain List =====\n\n")
    for domain in all_domains:
        f.write(domain + '\n')

print("✓ Successfully merged blocklists into youtube-blocklist.txt")
print(f"✓ New file size: {len(all_domains)} domains")
