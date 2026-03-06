#!/usr/bin/env python3
"""
split_social_blocklist.py

Read a blocklist file and split domains into separate files per social platform.

Usage:
  python split_social_blocklist.py -i blocker.txt -p youtube.com,tiktok.com,facebook.com -o social-blocks

The script extracts domain-like tokens from the input file and writes one file per pattern
(e.g. `social-blocks/youtube.txt`) containing matched domains (one per line). An
`other.txt` file is created for unmatched domains.
"""

from pathlib import Path
import argparse
import re
import sys

DOMAIN_RE = re.compile(r"(?:(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)\.)+[a-z]{2,}", re.I)


def extract_domains(text):
    domains = set()
    for match in DOMAIN_RE.findall(text):
        domains.add(match.lower())
    return domains


def normalize_pattern(pat: str) -> str:
    return pat.strip().lower()


def platform_name_from_pattern(pat: str) -> str:
    # e.g. youtube.com -> youtube
    first = pat.split(".")[0]
    return re.sub(r"[^a-z0-9_-]", "-", first.lower())


def split_domains(domains, patterns):
    result = {name: set() for name in patterns.keys()}
    others = set()
    for d in domains:
        matched = False
        for name, pats in patterns.items():
            for pat in pats:
                if d == pat or d.endswith("." + pat) or pat in d:
                    result[name].add(d)
                    matched = True
                    break
            if matched:
                break
        if not matched:
            others.add(d)
    return result, others


def main():
    parser = argparse.ArgumentParser(description="Split a blocklist into per-social-media files")
    parser.add_argument("-i", "--input", default="blocker.txt", help="Input blocklist file")
    parser.add_argument("-p", "--patterns", default="",
                        help="Comma-separated domain patterns (e.g. youtube.com,tiktok.com)")
    parser.add_argument("-o", "--out", default="social-blocks", help="Output folder")
    parser.add_argument("--main-out", default=None,
                        help="Write a filtered copy of the input file with social domains removed (path).")
    parser.add_argument("--inplace", action="store_true",
                        help="Overwrite the input file with social domains removed (unsafe).")
    parser.add_argument("--hosts-format", action="store_true",
                        help="Emit hosts-style lines (e.g. '0.0.0.0 domain') instead of plain domains")
    args = parser.parse_args()

    inp = Path(args.input)
    if not inp.exists():
        print(f"Input file not found: {inp}", file=sys.stderr)
        sys.exit(2)

    text = inp.read_text(encoding="utf-8", errors="replace")
    domains = extract_domains(text)
    if not domains:
        print("No domains found in input file.")
        sys.exit(0)

    raw_patterns = [normalize_pattern(x) for x in args.patterns.split(",") if x.strip()] if args.patterns else []

    if not raw_patterns:
        # default common platforms if none provided
        raw_patterns = ["youtube.com", "tiktok.com", "facebook.com", "instagram.com", "x.com", "twitter.com", "reddit.com"]

    patterns = {}
    for pat in raw_patterns:
        name = platform_name_from_pattern(pat)
        patterns.setdefault(name, []).append(pat)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    matched, others = split_domains(domains, patterns)

    def write_lines(path, lines):
        lines = sorted(lines)
        if args.hosts_format:
            content = "\n".join([f"0.0.0.0 {d}" for d in lines]) + ("\n" if lines else "")
        else:
            content = "\n".join(lines) + ("\n" if lines else "")
        path.write_text(content, encoding="utf-8")

    for name, ds in matched.items():
        out_path = out_dir / f"{name}.txt"
        write_lines(out_path, ds)
        print(f"Wrote {len(ds)} domains to {out_path}")

    other_path = out_dir / "other.txt"
    write_lines(other_path, others)
    print(f"Wrote {len(others)} domains to {other_path}")

    # Optionally write a filtered main blocker file without social domains
    matched_all = set().union(*matched.values())
    if args.main_out or args.inplace:
        # Filter original file lines by skipping lines that contain a matched domain as a whole token
        def line_contains_matched(line):
            for d in matched_all:
                # match whole domain token using word boundaries / non-word separators
                if re.search(r"(^|[^A-Za-z0-9-_.])" + re.escape(d) + r"($|[^A-Za-z0-9-_.])", line, re.I):
                    return True
            return False

        filtered_lines = [ln for ln in text.splitlines() if not line_contains_matched(ln)]
        target = Path(args.main_out) if args.main_out else inp
        target.write_text("\n".join(filtered_lines) + ("\n" if filtered_lines else ""), encoding="utf-8")
        print(f"Wrote filtered main file to {target} (removed {sum(1 for ln in text.splitlines() if line_contains_matched(ln))} lines)")

    # summary
    total = sum(len(s) for s in matched.values()) + len(others)
    print(f"Processed {total} domains in total.")


if __name__ == "__main__":
    main()
