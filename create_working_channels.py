#!/usr/bin/env python3

import urllib.request
import re

USER_AGENT = 'Mozilla/5.0 (compatible; IPTV-CHECKER/1.0)'
TIMEOUT = 5

def check_url(url):
    """Check if URL is accessible"""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT}, method='HEAD')
        with urllib.request.urlopen(req, timeout=TIMEOUT) as res:
            code = res.getcode()
            return 200 <= code < 300
    except Exception:
        # Try GET if HEAD fails
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as res:
                code = res.getcode()
                return 200 <= code < 300
        except:
            return False

def process_m3u(input_file, output_file=None):
    if output_file is None:
        output_file = input_file

    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    lines = content.split('\n')
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('#EXTINF'):
            extinf = line
            new_lines.append(extinf)
            i += 1
            if i < len(lines):
                url = lines[i].strip()
                new_lines.append(url)
                # Check if working
                if check_url(url):
                    # Change group-title to "Working Channels"
                    # Find group-title="..." and replace
                    pattern = r'group-title="[^"]*"'
                    if re.search(pattern, extinf):
                        new_extinf = re.sub(pattern, 'group-title="Working Channels"', extinf)
                        new_lines[-2] = new_extinf  # Replace the EXTINF line
                        print(f"Working: {url}")
                    else:
                        print(f"No group-title found for working channel: {url}")
                else:
                    print(f"Dead: {url}")
        else:
            new_lines.append(line)
        i += 1

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))

if __name__ == "__main__":
    process_m3u('/workspaces/PI-HOLE-BLOCK/working_channels/BD_channels.m3u')