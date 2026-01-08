"""
Export project architecture to both human-readable tree and JSON formats.

Usage:
  python export_architecture.py               # writes meta/architecture.json and meta/architecture.txt
  python export_architecture.py --root path  # scan `path` instead of cwd
  python export_architecture.py --json only  # write only JSON

Outputs:
  meta/architecture.json  - machine-friendly (recommended)
  meta/architecture.txt   - human-readable tree
"""

import os
import json
import argparse
from pathlib import Path
from typing import Dict, List

EXCLUDE_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", ".idea", ".vscode", "meta"}


def scan_directory(path: Path) -> Dict:
    node = {
        "name": path.name,
        "path": str(path.as_posix()),
        "type": "directory",
        "children": []
    }

    try:
        items = sorted(p for p in path.iterdir() if p.name not in EXCLUDE_DIRS)
    except PermissionError:
        return node

    for item in items:
        if item.is_dir():
            node["children"].append(scan_directory(item))
        else:
            try:
                size = item.stat().st_size
            except OSError:
                size = None
            node["children"].append({
                "name": item.name,
                "path": str(item.as_posix()),
                "type": "file",
                "extension": item.suffix,
                "size": size
            })

    return node


def generate_tree_lines(path: Path, prefix: str = "") -> List[str]:
    try:
        entries = sorted(e for e in path.iterdir() if e.name not in EXCLUDE_DIRS)
    except PermissionError:
        return [prefix + "[permission denied] " + path.name]

    lines: List[str] = []
    for i, entry in enumerate(entries):
        connector = "└── " if i == len(entries) - 1 else "├── "
        lines.append(prefix + connector + entry.name)
        if entry.is_dir():
            extension = "    " if i == len(entries) - 1 else "│   "
            lines.extend(generate_tree_lines(entry, prefix + extension))
    return lines


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export project architecture to JSON and TXT")
    parser.add_argument("--root", default='.', help="Root directory to scan")
    parser.add_argument("--json-only", action="store_true", dest="json_only", help="Write only JSON")
    parser.add_argument("--txt-only", action="store_true", dest="txt_only", help="Write only TXT")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    meta_dir = Path(root) / "meta"
    meta_dir.mkdir(exist_ok=True)

    print(f"Scanning root: {root}")

    architecture = scan_directory(root)

    json_path = meta_dir / "architecture.json"
    txt_path = meta_dir / "architecture.txt"

    if not args.txt_only:
        with json_path.open("w", encoding="utf-8") as f:
            json.dump(architecture, f, indent=2)
        print(f"Wrote: {json_path}")

    if not args.json_only:
        lines = generate_tree_lines(root)
        with txt_path.open("w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"Wrote: {txt_path}")

    print("Done.")
