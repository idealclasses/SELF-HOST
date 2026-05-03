#!/usr/bin/env python3
"""Split blocker.txt into separate section files.

Each section in blocker.txt is identified by a section heading comment, such as
"# Known Malware Domains". The script writes one file per section and preserves
any section metadata or source comments.
"""

from pathlib import Path
import argparse
import re


def normalize_section_title(title: str) -> str:
    title = title.strip().lstrip('#').strip()
    title = title.lower()
    title = re.sub(r"[\s&/]+", "_", title)
    title = re.sub(r"[^a-z0-9_]+", "", title)
    title = re.sub(r"_+", "_", title)
    return title.strip('_') or 'section'


def is_section_heading(line: str) -> bool:
    if not line.startswith('#'):
        return False
    text = line[1:].strip()
    if not text:
        return False
    if text.lower().startswith('source:'):
        return False
    if text.lower().startswith('total domains:'):
        return False
    return True


def split_blocker_file(input_path: Path, output_dir: Path):
    lines = input_path.read_text(encoding='utf-8', errors='ignore').splitlines()
    header_lines = []
    rest_lines = []
    seen_blank = False

    for line in lines:
        if not seen_blank:
            if line.strip() == '':
                seen_blank = True
                continue
            header_lines.append(line)
        else:
            rest_lines.append(line)

    sections = []
    current_section = None

    for line in rest_lines:
        if is_section_heading(line):
            if current_section is not None:
                sections.append(current_section)
            current_section = {'title': line, 'lines': [line]}
        else:
            if current_section is None:
                continue
            current_section['lines'].append(line)

    if current_section is not None:
        sections.append(current_section)

    output_dir.mkdir(parents=True, exist_ok=True)
    section_counts = []
    name_counts = {}

    if header_lines:
        header_path = output_dir / 'blocker_header.txt'
        header_path.write_text('\n'.join(header_lines).strip() + '\n', encoding='utf-8')
        section_counts.append(('blocker_header.txt', 0))

    for section in sections:
        section_name = normalize_section_title(section['title'])
        name_counts[section_name] = name_counts.get(section_name, 0) + 1
        if name_counts[section_name] > 1:
            section_name = f"{section_name}_{name_counts[section_name]}"
        path = output_dir / f"{section_name}.txt"

        path.write_text('\n'.join(section['lines']).strip() + '\n', encoding='utf-8')
        domain_count = sum(1 for l in section['lines'] if l and not l.startswith('#'))
        section_counts.append((path.name, domain_count))

    output_dir.mkdir(parents=True, exist_ok=True)
    section_counts = []
    name_counts = {}

    for section in sections:
        title = section['title']
        if title == 'header':
            path = output_dir / 'blocker_header.txt'
        else:
            section_name = normalize_section_title(title)
            name_counts[section_name] = name_counts.get(section_name, 0) + 1
            if name_counts[section_name] > 1:
                section_name = f"{section_name}_{name_counts[section_name]}"
            path = output_dir / f"{section_name}.txt"

        path.write_text('\n'.join(section['lines']).strip() + '\n', encoding='utf-8')
        domain_count = sum(1 for l in section['lines'] if l and not l.startswith('#'))
        section_counts.append((path.name, domain_count))

    summary_lines = [
        "# Split blocker.txt into section files",
        f"# Source: {input_path}",
        f"# Total sections: {len(section_counts)}",
        "",
    ]
    summary_lines += [f"{name}: {count} domain lines" for name, count in section_counts]
    summary_path = output_dir / 'split_summary.txt'
    summary_path.write_text('\n'.join(summary_lines) + '\n', encoding='utf-8')

    print(f"Created {len(section_counts)} files in {output_dir}")
    print(f"Summary written to {summary_path}")


def main():
    parser = argparse.ArgumentParser(description='Split blocker.txt into separate block list files')
    parser.add_argument('-i', '--input', default='blocker.txt', help='Input blocker file')
    parser.add_argument('-o', '--out', default='blocker_sections', help='Output directory')
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    split_blocker_file(input_path, Path(args.out))


if __name__ == '__main__':
    main()
