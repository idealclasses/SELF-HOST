#!/usr/bin/env python3
"""
Add tvg-id attributes to BD_channels.m3u using BD_epg.xml mappings.
"""
import re
from xml.etree import ElementTree as ET

EPG_FILE = 'BD_epg.xml'
M3U_FILE = 'BD_channels.m3u'
BACKUP_FILE = 'BD_channels.m3u.bak'

def normalize(name):
    s = name.lower()
    s = re.sub(r"\s+", " ", s)
    s = s.replace("|", "")
    s = s.replace("-", " ")
    s = s.strip()
    return s

# Parse EPG to build mapping from display-name -> channel id
epg_map = {}
try:
    tree = ET.parse(EPG_FILE)
    root = tree.getroot()
    for ch in root.findall('channel'):
        cid = ch.get('id')
        dn = ch.find('display-name')
        if dn is not None and cid:
            epg_map[normalize(dn.text)] = cid
except Exception as e:
    print('Failed to parse EPG:', e)

print(f'EPG mappings loaded: {len(epg_map)}')

# Read M3U
with open(M3U_FILE, 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

# Backup
with open(BACKUP_FILE, 'w', encoding='utf-8') as f:
    f.writelines(lines)

# Process and insert tvg-id when match found
out_lines = []
for i, line in enumerate(lines):
    if line.strip().startswith('#EXTINF'):
        ext = line.rstrip('\n')
        # skip if tvg-id already present
        if 'tvg-id=' in ext:
            out_lines.append(ext + '\n')
            continue
        # extract channel name after last comma
        if ',' in ext:
            name = ext.split(',')[-1].strip()
        else:
            name = ''
        key = normalize(name)
        tvgid = epg_map.get(key)
        if not tvgid:
            # try simple partial match
            for k,v in epg_map.items():
                if k in key or key in k:
                    tvgid = v
                    break
        if tvgid:
            # insert tvg-id before closing attributes or after -1
            # pattern: #EXTINF:-1 attr1="..." attr2="...",Channel Name
            m = re.match(r'(#EXTINF:)([^,]*)(,)(.*)', ext)
            if m:
                prefix, attrs, comma, chname = m.groups()
                # ensure attrs contains a space before adding
                new_attrs = attrs
                if new_attrs and not new_attrs.startswith(' '):
                    new_attrs = ' ' + new_attrs
                new_attrs = new_attrs + f' tvg-id="{tvgid}"'
                new_line = f"{prefix}{new_attrs}{comma}{chname}\n"
            else:
                # fallback: append tvg-id
                new_line = ext + f' tvg-id="{tvgid}"\n'
            out_lines.append(new_line)
        else:
            out_lines.append(ext + '\n')
    else:
        out_lines.append(line)

# Write back
with open(M3U_FILE, 'w', encoding='utf-8') as f:
    f.writelines(out_lines)

print('Completed tvg-id insertion. Backup saved to', BACKUP_FILE)
