#!/usr/bin/env python3

import subprocess
import re

# Mapping of channel names to YouTube handles
channel_mapping = {
    "BD | EKHON TV": "@ekhontvbd",
    "BD | Channel 24": "@channel24bd",
    "BD | Ekattor TV": "@ekattortvonline",
    "BD | Independent Television": "@independenttelevisionbd",
    "BD | DBC News": "@dbcnewsbd",
    "BD | NEWS24 Television": "@news24tvchannel",
    "BD | ATN News": "@atnnewsbd",
    "BD | SOMOY NEWS": "@somoynewsbd",
    "BD | News": "@banglanews24"
}

def get_hls_url(handle):
    try:
        result = subprocess.run(['yt-dlp', f'https://www.youtube.com/{handle}/live', '--get-url'], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print(f"Failed to get URL for {handle}: {result.stderr}")
            return None
    except Exception as e:
        print(f"Error getting URL for {handle}: {e}")
        return None

# Read the file
with open('/workspaces/PI-HOLE-BLOCK/BD_channels.m3u', 'r') as f:
    lines = f.readlines()

output = []
i = 0
while i < len(lines):
    line = lines[i].strip()
    if line.startswith('#EXTINF') and 'tvg-id="YouTube"' in line:
        # Extract channel name
        match = re.search(r',(.+)$', line)
        if match:
            channel_name = match.group(1).strip()
            if channel_name in channel_mapping:
                handle = channel_mapping[channel_name]
                hls_url = get_hls_url(handle)
                if hls_url:
                    output.append(line)
                    output.append(hls_url)
                    i += 2  # Skip the old URL
                    continue
    output.append(lines[i])
    i += 1

# Write back
with open('/workspaces/PI-HOLE-BLOCK/BD_channels.m3u', 'w') as f:
    f.writelines(line + '\n' for line in output)