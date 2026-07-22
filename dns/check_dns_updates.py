#!/usr/bin/env python3

from pathlib import Path
import urllib.request
from urllib.error import URLError, HTTPError
import time
import sys

USER_AGENT = 'Mozilla/5.0 (compatible; SELF-HOST/1.0)'
TIMEOUT = 10

def read_upstream_sources(file_path):
    """Read upstream DNS sources from file"""
    sources = []
    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                # Extract URL from lines like "https://... # comment"
                url = line.split('#')[0].strip()
                if url.startswith('http'):
                    sources.append(url)
        return sources
    except FileNotFoundError:
        print(f"Error: {file_path} not found")
        return []

def fetch_domains(url):
    """Fetch and parse domains from URL"""
    domains = set()
    try:
        print(f"  Fetching {url}...")
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
            content = response.read().decode('utf-8', errors='ignore')
        
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Parse different formats
            parts = line.split()
            if not parts:
                continue
            
            # Handle hosts file format (0.0.0.0 or 127.0.0.1)
            if parts[0] in ['0.0.0.0', '127.0.0.1']:
                if len(parts) >= 2:
                    domain = parts[1]
                else:
                    continue
            # Handle plain domain format
            elif parts[0].startswith(('http://', 'https://')):
                continue
            else:
                domain = parts[0]
            
            # Validate domain
            if domain and '.' in domain and not domain.startswith('^'):
                domains.add(domain.lower())
        
        return domains
    
    except (URLError, HTTPError, TimeoutError) as e:
        print(f"  ✗ Failed to fetch {url}: {e}")
        return set()
    except Exception as e:
        print(f"  ✗ Error processing {url}: {e}")
        return set()

def read_current_blocklist(file_path):
    """Read current blocker.txt domains"""
    domains = set()
    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                domain = line.lower()
                if '.' in domain:
                    domains.add(domain)
        return domains
    except FileNotFoundError:
        print(f"Warning: {file_path} not found")
        return set()

def main():
    print("=" * 70)
    print("DNS UPSTREAM SOURCES UPDATE CHECK")
    print("=" * 70)
    
    # Read upstream sources from this repo
    base_dir = Path(__file__).resolve().parent
    upstream_file = base_dir / 'upstream_dns.txt'
    sources = read_upstream_sources(upstream_file)
    
    if not sources:
        print("No upstream sources found!")
        return
    
    print(f"\nFound {len(sources)} upstream sources:\n")
    
    # Fetch all domains from upstream sources
    all_upstream_domains = set()
    for url in sources:
        domains = fetch_domains(url)
        print(f"  ✓ Found {len(domains)} domains")
        all_upstream_domains.update(domains)
        time.sleep(0.5)  # Rate limiting
    
    print(f"\n{'=' * 70}")
    print(f"Total unique domains from upstream sources: {len(all_upstream_domains)}")
    
    # Read current blocklist if available
    current_domains = set()
    blocker_file = None
    candidate_blockers = [
        base_dir.parent / 'blocklists' / 'blocker.txt',
        base_dir.parent / 'blocklists' / 'blocker_original.txt',
        base_dir.parent / 'blocklists' / 'blocker_cleaned.txt',
        base_dir.parent / 'blocklists' / 'blocker_medium.txt',
    ]
    for candidate in candidate_blockers:
        if candidate.exists():
            blocker_file = candidate
            break

    if blocker_file:
        current_domains = read_current_blocklist(blocker_file)
        print(f"Current domains in {blocker_file}: {len(current_domains)}")
    else:
        print("No local blocklist file found; only generating upstream_blocklist.txt")

    # Write aggregated upstream blocklist
    output_file = base_dir / 'upstream_blocklist.txt'
    with open(output_file, 'w', encoding='utf-8') as out_f:
        out_f.write('# Aggregated upstream domain list generated from dns/upstream_dns.txt\n')
        out_f.write(f'# Sources: {len(sources)}\n')
        out_f.write('# Broken sources are excluded.\n')
        for domain in sorted(all_upstream_domains):
            out_f.write(domain + '\n')
    print(f"Wrote aggregated upstream blocklist to {output_file}")
    
    # Find new domains
    new_domains = all_upstream_domains - current_domains
    print(f"\n{'=' * 70}")
    print(f"NEW DOMAINS FOUND: {len(new_domains)}")
    print(f"{'=' * 70}\n")
    
    if not new_domains:
        print("✓ No new domains found. Your local blocklist is up to date!")
        print(f"{'=' * 70}\n")
        return

    # Sort and display new domains
    sorted_new = sorted(new_domains)
    print("Top 50 new domains:")
    for i, domain in enumerate(sorted_new[:50], 1):
        print(f"  {i:3d}. {domain}")
    
    if len(sorted_new) > 50:
        print(f"\n... and {len(sorted_new) - 50} more")

    if blocker_file:
        print(f"\n{'=' * 70}")
        print(f"Would you like to add these {len(new_domains)} new domains to {blocker_file.name}?")
        print("(This will append to the existing file)")

        response = input(f"\nAdd new domains to {blocker_file.name}? (y/n): ").strip().lower()
        if response == 'y':
            try:
                with open(blocker_file, 'a', encoding='utf-8') as f:
                    f.write('\n# New domains added from upstream sources\n')
                    for domain in sorted_new:
                        f.write(domain + '\n')
                print(f"\n✓ Added {len(new_domains)} new domains to {blocker_file}")
            except Exception as e:
                print(f"✗ Error writing to {blocker_file}: {e}")
        else:
            print("\nUpdate cancelled.")
    else:
        print("No local blocklist file available to update automatically.")
        print(f"Use {output_file} or add one of these domains to your preferred local blocklist manually.")

    print(f"{'=' * 70}\n")

if __name__ == '__main__':
    main()
