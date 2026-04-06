#!/usr/bin/env python3

import re
import urllib.request
from urllib.error import URLError, HTTPError
from pathlib import Path

USER_AGENT = 'Mozilla/5.0 (compatible; IPTV-CHECKER/1.0)'
TIMEOUT = 15
UPSTREAM_SOURCES = Path('/workspaces/PI-HOLE-BLOCK/dns/upstream_sources.txt')
OUTPUT_FILE = Path('/workspaces/PI-HOLE-BLOCK/working_channels/BD_channels.m3u')


def fetch_url(url):
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as res:
        return res.read().decode('utf-8', errors='ignore')


def parse_m3u(content):
    lines = content.split('\n')
    entries = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('#EXTINF'):
            extinf = line
            url = ''
            i += 1
            if i < len(lines):
                url = lines[i].strip()
            if url:
                entries.append((extinf, url))
        i += 1
    return entries


def channel_name(extinf):
    comma = extinf.rfind(',')
    return extinf[comma + 1 :].strip() if comma != -1 else extinf.strip()


def set_group_title(extinf, title):
    if 'group-title=' in extinf:
        return re.sub(r'group-title="[^"]*"', f'group-title="{title}"', extinf)

    if extinf.startswith('#EXTINF'):
        parts = extinf.split(',', 1)
        if len(parts) == 2:
            return f'{parts[0]} group-title="{title}",{parts[1]}'

    return extinf


def is_url_working(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT}, method='HEAD')
        with urllib.request.urlopen(req, timeout=TIMEOUT) as res:
            code = res.getcode()
            if 200 <= code < 300:
                return True
    except Exception:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as res:
                code = res.getcode()
                if 200 <= code < 300:
                    try:
                        data = res.read(1024)
                        return len(data) > 0
                    except Exception:
                        return True
        except (HTTPError, URLError, TimeoutError, ValueError):
            return False
    return False


def load_sources():
    if not UPSTREAM_SOURCES.exists():
        raise FileNotFoundError(f'{UPSTREAM_SOURCES} not found')
    text = UPSTREAM_SOURCES.read_text(encoding='utf-8', errors='ignore')
    return [line.strip() for line in text.splitlines() if line.strip() and not line.strip().startswith('#')]


def write_m3u(path, entries):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8') as f:
        f.write('#EXTM3U\n')
        for extinf, url in entries:
            f.write(extinf + '\n')
            f.write(url + '\n')


def build_playlists():
    sources = load_sources()
    unique_entries = {}

    for src in sources:
        try:
            data = fetch_url(src)
            entries = parse_m3u(data)
            print(f'Fetched {len(entries)} entries from {src}')
            for extinf, url in entries:
                key = (channel_name(extinf).lower(), url)
                if key not in unique_entries:
                    unique_entries[key] = (extinf, url)
        except Exception as exc:
            print(f'Failed to fetch {src}: {exc}')

    output_entries = []
    for extinf, url in unique_entries.values():
        if is_url_working(url):
            output_entries.append((set_group_title(extinf, 'Working Channels'), url))
            print(f'Working: {channel_name(extinf)}')
        else:
            output_entries.append((extinf, url))
            print(f'Dead: {channel_name(extinf)}')

    write_m3u(OUTPUT_FILE, output_entries)
    print(f'Wrote combined playlist: {len(output_entries)} entries to {OUTPUT_FILE}')


if __name__ == '__main__':
    build_playlists()