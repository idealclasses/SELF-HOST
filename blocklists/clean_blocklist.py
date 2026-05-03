#!/usr/bin/env python3
"""
Clean blocker.txt by removing whitelisted domains that are essential for normal internet usage
"""

import os

def load_whitelist(whitelist_file):
    """Load whitelist from file"""
    whitelist = set()
    if os.path.exists(whitelist_file):
        with open(whitelist_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Remove any patterns like || and ^
                    if line.startswith('||') and line.endswith('^'):
                        line = line[2:-1]
                    # Handle wildcards by taking the domain part
                    if '*' in line:
                        # For now, just add the domain after the wildcard
                        parts = line.split('*')
                        if len(parts) > 1:
                            line = parts[-1].lstrip('.')
                    whitelist.add(line.lower())
    return whitelist

WHITELIST = load_whitelist('whitelisted_domains.txt')

def is_whitelisted(domain):
    """Check if a domain should be whitelisted (not blocked)"""
    domain = domain.lower().strip()
    
    # Handle regex patterns (remove || and ^)
    if domain.startswith('||') and domain.endswith('^'):
        domain = domain[2:-1]
    
    # Check exact match or subdomain match
    if domain in WHITELIST:
        return True
    
    # Check subdomain matches
    for whitelisted in WHITELIST:
        if domain.endswith('.' + whitelisted):
            return True
    
    return False

def clean_blocklist(input_file, output_file, removed_file):
    """Clean the blocklist by removing whitelisted domains"""
    cleaned_domains = []
    removed_domains = []
    removed_count = 0

    try:
        with open(input_file, 'r') as f:
            for line in f:
                line_stripped = line.strip()
                if not line_stripped or line_stripped.startswith('#'):
                    cleaned_domains.append(line)
                    continue

                if is_whitelisted(line_stripped):
                    removed_count += 1
                    removed_domains.append(line_stripped)
                    print(f"Removed whitelisted domain: {line_stripped}")
                else:
                    cleaned_domains.append(line)

        # Update the header with new count
        header_updated = False
        for i, line in enumerate(cleaned_domains):
            if line.startswith('# Total unique domains:'):
                # Count actual domains
                domain_count = sum(1 for l in cleaned_domains if l.strip() and not l.startswith('#'))
                cleaned_domains[i] = f'# Total unique domains: {domain_count}\n'
                header_updated = True
                break

        with open(output_file, 'w') as f:
            f.writelines(cleaned_domains)

        # Write removed domains to separate file
        with open(removed_file, 'w') as f:
            f.write("# Whitelisted domains removed from blocker.txt\n")
            f.write(f"# Total removed: {len(removed_domains)}\n")
            f.write("# Date: 2026-03-13\n\n")
            for domain in sorted(removed_domains):
                f.write(domain + '\n')

        print(f"\nCleaning complete:")
        print(f"Removed {removed_count} whitelisted domains")
        print(f"Remaining domains: {sum(1 for l in cleaned_domains if l.strip() and not l.startswith('#'))}")
        print(f"Cleaned blocklist saved to: {output_file}")
        print(f"Removed domains recorded in: {removed_file}")

    except Exception as e:
        print(f"Error cleaning blocklist: {e}")

if __name__ == "__main__":
    clean_blocklist('blocker.txt', 'blocker_cleaned.txt', 'removed_domains.txt')