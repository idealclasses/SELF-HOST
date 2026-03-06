#!/usr/bin/env python3
import os
import shutil
from pathlib import Path

base_path = Path('/workspaces/PI-HOLE-BLOCK')

# Define file organization structure
file_mapping = {
    'dns': [
        'upstream_dns.txt',
        'upstream_sources.txt',
        'check_dns_updates.py'
    ],
    'iptv': [
        'BD_channels.m3u.bak',
        'check_iptv_links.py',
        'add_tvgid.py',
        'create_working_channels.py',
        'combine_bd.py',
        'extract_bd.py',
        'update_bd_channels.py',
        'update_bd_channels_enhanced.py',
        'update_youtube_urls.py'
    ],
    'blocklists': [
        'blocker.txt',
        'social-block.txt',
        'youtube-blocklist-merged.txt',
        'merge_blocklists.py',
        'split_social_blocklist.py'
    ],
    'docs': [
        'README.md',
        'SOCIAL_SPLIT.md'
    ],
    'images': [
        'Copilot_20260127_010822.png'
    ],
    'scripts': [
        'check_and_add_hutho.py',
        'check_and_add_saifujjaman.py'
    ]
}

# Move files to their designated folders
moved_count = 0
for folder, files in file_mapping.items():
    folder_path = base_path / folder
    folder_path.mkdir(exist_ok=True)
    
    for file in files:
        src = base_path / file
        dst = folder_path / file
        
        if src.exists():
            try:
                shutil.move(str(src), str(dst))
                print(f"✓ Moved: {file} → {folder}/")
                moved_count += 1
            except Exception as e:
                print(f"✗ Error moving {file}: {e}")
        else:
            print(f"- Skipped: {file} (not found)")

print(f"\n✓ Successfully organized {moved_count} files!")
print("\nOrganization Summary:")
print("├── dns/          - DNS configuration and related scripts")
print("├── iptv/         - IPTV/M3U playlist files and scripts")
print("├── blocklists/   - DNS blocklists and related scripts")
print("├── docs/         - Documentation files")
print("├── images/       - Image files")
print("└── scripts/      - Utility scripts")
