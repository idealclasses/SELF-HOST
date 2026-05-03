#!/usr/bin/env python3
"""Create a smaller version of blocker.txt by removing large sections."""

from pathlib import Path

def create_smaller_blocklist(sections_dir: Path, output_path: Path):
    """Merge selected sections to create a smaller blocklist."""
    # Sections to keep (exclude large ones)
    keep_sections = {
        'blocker_header.txt',
        'known_malware_domains.txt',
        'popup_and_ad_networks.txt',
        'adware_and_pup_potentially_unwanted_programs.txt',
        'botnet_and_c_c_servers.txt',
        'exploit_kits_and_attack_servers.txt',
        'tracking_and_analytics_privacy_concerns.txt',
        'additional_trackers_and_analytics_endpoints_added_to_improve_coverage.txt',
        'ppc_and_affiliate_networks.txt',
        'phishing_and_scam_domains.txt',
        'gambling_and_betting_websites.txt',
        'bangladesh_gambling_and_betting_sites.txt',
        'content_delivery_networks_and_ad_click_hosts.txt',
        'cryptomining_and_botnets.txt',
        'youtube_ads_adrelated_domains_safe_blocking.txt',
        'google_advertising_services_ad_serving_only.txt',
        'security_threats.txt',
        'local_ipv6_helper_names_and_teredo_were_removed_to_avoid_breaking_connectivity.txt'
    }

    lines = []
    for file_path in sorted(sections_dir.glob('*.txt')):
        if file_path.name in keep_sections:
            content = file_path.read_text(encoding='utf-8', errors='ignore').strip()
            if content:
                lines.append(content)
                lines.append('')  # Add blank line between sections

    # Remove trailing blank lines
    while lines and lines[-1] == '':
        lines.pop()

    output_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f"Created smaller blocklist: {output_path}")
    print(f"Total lines: {len(lines)}")

if __name__ == '__main__':
    sections_dir = Path('blocklists/blocker_sections')
    output_path = Path('blocklists/blocker_small.txt')
    create_smaller_blocklist(sections_dir, output_path)