#!/usr/bin/env python3

with open('/workspaces/PI-HOLE-BLOCK/YT_playlist.m3u', 'r') as f:
    lines = f.readlines()

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