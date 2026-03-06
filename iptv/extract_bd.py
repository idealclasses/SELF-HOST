#!/usr/bin/env python3

import urllib.request

# Download the playlist
url = "https://raw.githubusercontent.com/time2shine/IPTV/refs/heads/master/combined.m3u"
response = urllib.request.urlopen(url)
data = response.read().decode('utf-8')
lines = data.split('\n')

output = ['#EXTM3U\n']

i = 0
while i < len(lines):
    line = lines[i].strip()
    if line.startswith('#EXTINF') and 'BD |' in line:
        output.append(line + '\n')
        i += 1
        if i < len(lines):
            output.append(lines[i])
    i += 1

with open('/workspaces/PI-HOLE-BLOCK/BD_channels.m3u', 'w') as f:
    f.writelines(output)