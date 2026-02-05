#!/usr/bin/env python3
"""
Fetch a web page and extract .m3u/.m3u8 links.

Usage:
  python3 scripts/extract_m3u_from_page.py <url> [--build OUTPUT.m3u] [--header "Key: Value"] [--cookie "name=value"]

Options:
  --build FILE    Build an #EXTM3U file using the discovered links (names are inferred from nearby text or URL path)
  --header H      Add a custom header (can be repeated)
  --cookie C      Add a cookie header (can be repeated)
  --timeout S     Timeout in seconds (default 10)

Notes:
  - This script uses only the Python standard library so you can run it locally without extra deps.
  - If the page is not reachable from this environment (e.g., local ISP link), run it on your machine inside the same network.
"""

import argparse
import re
import sys
import urllib.request
import urllib.parse
import socket
from urllib.error import URLError, HTTPError
from html import unescape


def fetch(url, headers=None, timeout=10):
    headers = headers or {}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as res:
        return res.read().decode('utf-8', errors='ignore')


def find_links(html, base_url):
    # Find absolute links
    abs_links = re.findall(r"https?://[^\"' >]+?\.(?:m3u8?|m3u)", html, flags=re.IGNORECASE)
    # Find src/href relative
    rel_links = re.findall(r"(?:src|href)=\"(/[^\"']+?\.(?:m3u8?|m3u))\"", html, flags=re.IGNORECASE)
    links = []
    for l in abs_links:
        links.append(l)
    for l in rel_links:
        links.append(urllib.parse.urljoin(base_url, l))

    # Also look for URLs without quote context
    other = re.findall(r"\b/[^\s\"'<>]+?\.(?:m3u8?|m3u)\b", html, flags=re.IGNORECASE)
    for l in other:
        full = urllib.parse.urljoin(base_url, l)
        if full not in links:
            links.append(full)

    # Deduplicate while preserving order
    seen = set()
    uniq = []
    for l in links:
        if l not in seen:
            seen.add(l)
            uniq.append(l)
    return uniq


def infer_name(html, link):
    # Try to find a nearby label for the link in the HTML
    # Search for up to 200 chars before the link
    esc = re.escape(link)
    m = re.search(r"(.{0,200})" + esc, html)
    if m:
        chunk = m.group(1)
        # Remove tags and newlines
        text = re.sub(r"<[^>]+>", " ", chunk)
        text = unescape(text).strip()
        text = re.sub(r"\s+", " ", text)
        # Take last few words as candidate
        if text:
            words = text.split()[-6:]
            cand = ' '.join(words).strip(' ,:-')
            if len(cand) > 0:
                return cand
    # Fallback to last path component
    path = urllib.parse.urlparse(link).path
    name = path.rstrip('/').split('/')[-1]
    return name


def build_m3u(html, links):
    out = ["#EXTM3U"]
    for l in links:
        name = infer_name(html, l)
        out.append(f"#EXTINF:-1,{name}")
        out.append(l)
    return '\n'.join(out) + '\n'


def main():
    p = argparse.ArgumentParser()
    p.add_argument('url')
    p.add_argument('--build', help='Output M3U file path')
    p.add_argument('--header', action='append', help='Add a header, format: "Key: Value"')
    p.add_argument('--cookie', action='append', help='Add cookie, format: "name=value"')
    p.add_argument('--timeout', type=int, default=10)
    p.add_argument('--check', action='store_true', help='Verify each discovered stream URL for liveliness')
    p.add_argument('--report', help='Write a simple check report to this file')

    args = p.parse_args()
    headers = {'User-Agent': 'curl/7.88.1'}
    if args.header:
        for h in args.header:
            if ':' in h:
                k, v = h.split(':', 1)
                headers[k.strip()] = v.strip()
    if args.cookie:
        headers['Cookie'] = '; '.join(args.cookie)

    try:
        html = fetch(args.url, headers=headers, timeout=args.timeout)
    except Exception as e:
        print('ERROR fetching URL:', e, file=sys.stderr)
        sys.exit(2)

    links = find_links(html, args.url)
    if not links:
        print('No .m3u/.m3u8 links found on the page')
        sys.exit(0)

    print('Found links:')
    for l in links:
        print(l)

    # If --check supplied, verify each URL's liveliness
    def is_url_working(url, timeout=args.timeout):
        # Try HEAD, then small GET
        try:
            req = urllib.request.Request(url, headers=headers, method='HEAD')
            with urllib.request.urlopen(req, timeout=timeout) as res:
                code = res.getcode()
                if 200 <= code < 300:
                    return True
        except Exception:
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=timeout) as res:
                    code = res.getcode()
                    try:
                        _ = res.read(1024)
                    except Exception:
                        pass
                    if 200 <= code < 300:
                        return True
            except (HTTPError, URLError, socket.timeout, ValueError):
                return False
        return False

    report_lines = []
    if args.check:
        print('\nChecking links liveliness:')
        for l in links:
            try:
                ok = is_url_working(l)
            except Exception as e:
                ok = False
            status = 'OK' if ok else 'FAILED'
            print(f"  {status}: {l}")
            report_lines.append(f"{status}, {l}")
        if args.report:
            with open(args.report, 'w') as rf:
                rf.write('\n'.join(report_lines) + '\n')
            print('\nWrote report to', args.report)

    if args.build:
        m3u = build_m3u(html, links)
        with open(args.build, 'w') as f:
            f.write(m3u)
        print('\nWrote M3U to', args.build)


if __name__ == '__main__':
    main()
